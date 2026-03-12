#!/usr/bin/env python3
"""Risk Trend Analysis.

Analyzes historical risk scores and generates trend reports.

Outputs:
- reports/trend-<YYYYMM>.json (monthly trend data)
- reports/trend-report-<ts>.md (human readable summary)
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
CURRENT_MONTH = time.strftime("%Y%m")
OUT_JSON = REPORTS / f"trend-{CURRENT_MONTH}.json"
OUT_MD = REPORTS / f"trend-report-{TS}.md"


def load_risk_scores() -> List[Dict[str, Any]]:
    """Load all historical risk score reports."""
    scores = []
    for f in sorted(REPORTS.glob("risk-score-*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            scores.append({
                "time": data.get("time", ""),
                "score": data.get("score", 0),
                "level": data.get("level", "UNKNOWN"),
                "breakdown": data.get("breakdown", []),
            })
        except Exception:
            pass
    return scores


def load_drift_history() -> List[Dict[str, Any]]:
    """Load historical config drift reports."""
    drifts = []
    for f in sorted(REPORTS.glob("config-drift-*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            drifts.append({
                "time": data.get("time", ""),
                "total": data.get("summary", {}).get("total", 0),
                "critical": data.get("summary", {}).get("critical", 0),
            })
        except Exception:
            pass
    return drifts


def load_threat_intel_history() -> List[Dict[str, Any]]:
    """Load historical threat intel reports."""
    intel = []
    for f in sorted(REPORTS.glob("threat-intel-*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            intel.append({
                "time": data.get("time", ""),
                "total": data.get("summary", {}).get("total", 0),
                "critical": data.get("summary", {}).get("critical", 0),
                "high": data.get("summary", {}).get("high", 0),
            })
        except Exception:
            pass
    return intel


def calculate_trend(scores: List[Dict]) -> Dict[str, Any]:
    """Calculate risk score trend."""
    if len(scores) < 2:
        return {
            "direction": "stable",
            "change": 0,
            "change_percent": 0,
        }

    # Compare first and last
    first = scores[0]["score"]
    last = scores[-1]["score"]

    change = last - first
    change_percent = (change / first * 100) if first > 0 else 0

    if change < -10:
        direction = "improving_fast"
    elif change < 0:
        direction = "improving"
    elif change > 10:
        direction = "worsening_fast"
    elif change > 0:
        direction = "worsening"
    else:
        direction = "stable"

    return {
        "direction": direction,
        "change": change,
        "change_percent": round(change_percent, 1),
        "first_score": first,
        "last_score": last,
        "data_points": len(scores),
    }


def get_monthly_summary(scores: List[Dict]) -> Dict[str, Any]:
    """Get summary for current month."""
    current_month_scores = [
        s for s in scores
        if s["time"].startswith(time.strftime("%Y-%m"))
    ]

    if not current_month_scores:
        return {
            "average": 0,
            "min": 0,
            "max": 0,
            "best_day": None,
            "worst_day": None,
        }

    score_values = [s["score"] for s in current_month_scores]
    avg = sum(score_values) / len(score_values)

    best = min(current_month_scores, key=lambda x: x["score"])
    worst = max(current_month_scores, key=lambda x: x["score"])

    return {
        "average": round(avg, 1),
        "min": min(score_values),
        "max": max(score_values),
        "best_day": best["time"][:10] if best else None,
        "worst_day": worst["time"][:10] if worst else None,
        "readings": len(current_month_scores),
    }


def gen_md_report(
    scores: List[Dict],
    drifts: List[Dict],
    intel: List[Dict],
    trend: Dict,
    monthly: Dict,
) -> str:
    """Generate human-readable markdown trend report."""
    lines = []
    lines.append("# 📈 Risk Trend Analysis")
    lines.append(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Overall trend
    lines.append("## Overall Trend")
    emoji = {
        "improving_fast": "🚀",
        "improving": "✅",
        "stable": "➡️",
        "worsening": "⚠️",
        "worsening_fast": "🔴",
    }.get(trend["direction"], "❓")

    lines.append(f"- **Direction**: {emoji} {trend['direction'].replace('_', ' ').title()}")
    lines.append(f"- **Change**: {trend['change']:+d} points ({trend['change_percent']:+.1f}%)")
    lines.append(f"- **From**: {trend.get('first_score', 'N/A')} → **To**: {trend.get('last_score', 'N/A')}")
    lines.append(f"- **Data Points**: {trend.get('data_points', 0)}")
    lines.append("")

    # Monthly summary
    lines.append("## This Month's Summary")
    lines.append(f"- **Average Score**: {monthly['average']}")
    lines.append(f"- **Best**: {monthly['min']} (on {monthly['best_day']})")
    lines.append(f"- **Worst**: {monthly['max']} (on {monthly['worst_day']})")
    lines.append(f"- **Readings**: {monthly['readings']}")
    lines.append("")

    # Key improvements
    if trend["direction"] in ("improving", "improving_fast"):
        lines.append("## 🎉 Key Improvements")
        lines.append("Your security posture is improving! Keep up the good work.")
        lines.append("")

    # Areas to improve
    if trend["direction"] in ("worsening", "worsening_fast"):
        lines.append("## ⚠️ Areas Needing Attention")
        lines.append("Your risk score is increasing. Consider:")
        lines.append("- Reviewing critical findings in recent reports")
        lines.append("- Applying recommended fixes")
        lines.append("- Running `auto_fix.py` for automatic remediation")
        lines.append("")

    # Recent activity
    if drifts:
        recent_drifts = drifts[-5:]
        avg_drifts = sum(d["total"] for d in recent_drifts) / len(recent_drifts) if recent_drifts else 0
        lines.append("## 📊 Configuration Drift (Last 5 Readings)")
        lines.append(f"- **Average Drifts**: {avg_drifts:.1f}")
        lines.append(f"- **Latest**: {recent_drifts[-1]['total'] if recent_drifts else 0} ({recent_drifts[-1]['critical'] if recent_drifts else 0} critical)")
        lines.append("")

    if intel:
        recent_intel = intel[-5:]
        avg_vulns = sum(i["total"] for i in recent_intel) / len(recent_intel) if recent_intel else 0
        lines.append("## 🦠 Vulnerability Intelligence (Last 5 Readings)")
        lines.append(f"- **Average Vulns**: {avg_vulns:.1f}")
        lines.append(f"- **Latest**: {recent_intel[-1]['total'] if recent_intel else 0} ({recent_intel[-1]['critical'] if recent_intel else 0} critical)")
        lines.append("")

    # Trend chart (ASCII art)
    if len(scores) >= 5:
        lines.append("## 📉 Score History (Last 10 Readings)")
        last_10 = scores[-10:] if len(scores) >= 10 else scores
        max_score = max(s["score"] for s in last_10) if last_10 else 100

        for s in last_10:
            bar_len = int((s["score"] / max_score) * 30) if max_score > 0 else 0
            bar = "█" * bar_len + "░" * (30 - bar_len)
            level_emoji = {
                "LOW": "🟢",
                "MEDIUM": "🟡",
                "HIGH": "🟠",
                "CRITICAL": "🔴",
            }.get(s.get("level", ""), "⚪")
            lines.append(f"{s['time'][:16]} {level_emoji} {s['score']:3d} {bar}")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by openclaw-guardrails trend_analysis.py*")

    return "\n".join(lines)


def main() -> int:
    print("📈 Analyzing risk trends...")

    # Load historical data
    print("  - Loading risk scores...")
    scores = load_risk_scores()
    print(f"    Found: {len(scores)} readings")

    print("  - Loading config drift history...")
    drifts = load_drift_history()
    print(f"    Found: {len(drifts)} readings")

    print("  - Loading threat intel history...")
    intel = load_threat_intel_history()
    print(f"    Found: {len(intel)} readings")

    # Calculate trends
    trend = calculate_trend(scores)
    monthly = get_monthly_summary(scores)

    # Save monthly trend data (append mode)
    monthly_data = {
        "month": CURRENT_MONTH,
        "scores": scores,
        "trend": trend,
        "monthly_summary": monthly,
    }

    # Load existing monthly data if present
    if OUT_JSON.exists():
        try:
            existing = json.loads(OUT_JSON.read_text(encoding="utf-8"))
            # Keep only current month's scores
            existing["scores"] = scores
            existing["trend"] = trend
            existing["monthly_summary"] = monthly
            monthly_data = existing
        except Exception:
            pass

    OUT_JSON.write_text(json.dumps(monthly_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Generate MD report
    md_report = gen_md_report(scores, drifts, intel, trend, monthly)
    OUT_MD.write_text(md_report, encoding="utf-8")

    print(f"\n✅ Saved: {OUT_JSON}")
    print(f"✅ Saved: {OUT_MD}")

    # Print summary
    print(f"\n📊 Trend Summary:")
    print(f"  Direction: {trend['direction'].replace('_', ' ').title()}")
    print(f"  Change: {trend['change']:+d} points ({trend['change_percent']:+.1f}%)")
    print(f"  This Month Avg: {monthly['average']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
