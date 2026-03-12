#!/usr/bin/env python3
"""HTML Dashboard Generator.

Creates an interactive HTML report with:
- Risk score gauge (red/yellow/green)
- Historical trend chart (Chart.js)
- Actionable findings list
- One-click copy fix commands

Outputs:
- reports/dashboard-<ts>.html
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
OUT_HTML = REPORTS / f"dashboard-{TS}.html"


def load_latest_report(pattern: str) -> Optional[Dict]:
    """Load latest report matching pattern."""
    files = sorted(REPORTS.glob(pattern))
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def load_risk_history() -> List[Dict]:
    """Load last 30 risk score readings."""
    scores = []
    for f in sorted(REPORTS.glob("risk-score-*.json"))[-30:]:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            scores.append({
                "time": data.get("time", "")[:16],
                "score": data.get("score", 0),
                "level": data.get("level", ""),
            })
        except Exception:
            pass
    return scores


def generate_html(
    risk_score: Optional[Dict],
    drift: Optional[Dict],
    intel: Optional[Dict],
    history: List[Dict],
) -> str:
    """Generate interactive HTML dashboard."""

    # Get current values
    score = risk_score.get("score", 0) if risk_score else 0
    level = risk_score.get("level", "UNKNOWN") if risk_score else "UNKNOWN"

    drift_total = drift.get("summary", {}).get("total", 0) if drift else 0
    drift_critical = drift.get("summary", {}).get("critical", 0) if drift else 0

    vuln_total = intel.get("summary", {}).get("total", 0) if intel else 0
    vuln_critical = intel.get("summary", {}).get("critical", 0) if intel else 0

    # Color based on score
    if score >= 80:
        score_color = "#22c55e"  # green
        score_bg = "bg-green-500"
    elif score >= 60:
        score_color = "#eab308"  # yellow
        score_bg = "bg-yellow-500"
    elif score >= 40:
        score_color = "#f97316"  # orange
        score_bg = "bg-orange-500"
    else:
        score_color = "#ef4444"  # red
        score_bg = "bg-red-500"

    # Get fixes from risk_score report
    fixes = []
    if risk_score:
        breakdown = risk_score.get("breakdown", [])
        for b in breakdown:
            if b.get("deduction", 0) > 0:
                fixes.append(f"• {b['category']}: -{b['deduction']} pts ({b.get('critical', 0)} critical)")

    # History chart data
    chart_labels = [h["time"] for h in history]
    chart_data = [h["score"] for h in history]

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Guardrails Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gauge {{
            width: 200px;
            height: 100px;
            position: relative;
            display: inline-block;
        }}
        .gauge-fill {{
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 180px;
            height: 90px;
            border-radius: 90px 90px 0 0;
            background: conic-gradient(from 180deg at 50% 100%, {score_color} {score}%, #e5e7eb {score}%);
        }}
        .gauge-center {{
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 140px;
            height: 70px;
            background: white;
            border-radius: 70px 70px 0 0;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            padding-bottom: 10px;
            font-size: 32px;
            font-weight: bold;
            color: {score_color};
        }}
    </style>
</head>
<body class="bg-gray-100 min-h-screen p-8">
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h1 class="text-3xl font-bold text-gray-800">🛡️ OpenClaw Guardrails Dashboard</h1>
            <p class="text-gray-600 mt-2">Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <!-- Risk Score Gauge -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Current Risk Score</h2>
            <div class="text-center">
                <div class="gauge">
                    <div class="gauge-fill"></div>
                    <div class="gauge-center">{score}</div>
                </div>
                <p class="mt-4 text-lg font-semibold {score_bg.replace('bg-', 'text-')}">{level}</p>
                <div class="mt-4 flex justify-center gap-4 text-sm text-gray-600">
                    <span class="flex items-center">🟢 80-100 LOW</span>
                    <span class="flex items-center">🟡 60-79 MEDIUM</span>
                    <span class="flex items-center">🟠 40-59 HIGH</span>
                    <span class="flex items-center">🔴 0-39 CRITICAL</span>
                </div>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <!-- Config Drift -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">📊 Config Drift</h3>
                <p class="text-4xl font-bold text-red-500">{drift_critical}</p>
                <p class="text-gray-600 mt-2">Critical drifts (of {drift_total} total)</p>
            </div>

            <!-- Vulnerabilities -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">🦠 Vulnerabilities</h3>
                <p class="text-4xl font-bold text-orange-500">{vuln_critical}</p>
                <p class="text-gray-600 mt-2">Critical (of {vuln_total} total)</p>
            </div>

            <!-- Findings -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">🔍 Findings</h3>
                <p class="text-4xl font-bold text-blue-500">{len(fixes)}</p>
                <p class="text-gray-600 mt-2">Categories with deductions</p>
            </div>
        </div>

        <!-- Trend Chart -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Risk Score Trend (Last 30 Days)</h2>
            <canvas id="trendChart" height="80"></canvas>
        </div>

        <!-- Action Items -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">🔧 Recommended Actions</h2>
            <ul class="space-y-2">
                {''.join(f'<li class="flex items-start"><span class="text-red-500 mr-2">•</span><span class="text-gray-700">{fix}</span></li>' for fix in fixes) or '<li class="text-gray-500">No immediate actions required</li>'}
            </ul>
        </div>

        <!-- Quick Commands -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">⚡ Quick Commands</h2>
            <div class="space-y-3">
                <div class="flex items-center justify-between bg-gray-50 rounded p-3">
                    <code class="text-sm text-gray-700">python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py</code>
                    <button onclick="navigator.clipboard.writeText('python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py')" class="text-blue-500 hover:text-blue-700 text-sm">Copy</button>
                </div>
                <div class="flex items-center justify-between bg-gray-50 rounded p-3">
                    <code class="text-sm text-gray-700">python3 ~/.openclaw/skills/openclaw-guardrails/scripts/auto_fix.py</code>
                    <button onclick="navigator.clipboard.writeText('python3 ~/.openclaw/skills/openclaw-guardrails/scripts/auto_fix.py')" class="text-blue-500 hover:text-blue-700 text-sm">Copy</button>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center text-gray-500 text-sm mt-8">
            Generated by openclaw-guardrails html_dashboard.py
        </div>
    </div>

    <script>
        // Trend Chart
        const ctx = document.getElementById('trendChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(chart_labels)},
                datasets: [{{
                    label: 'Risk Score',
                    data: {json.dumps(chart_data)},
                    borderColor: '{score_color}',
                    backgroundColor: '{score_color}20',
                    fill: true,
                    tension: 0.4,
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                if (value >= 80) return '🟢';
                                if (value >= 60) return '🟡';
                                if (value >= 40) return '🟠';
                                return '🔴';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Score: ' + context.parsed.y;
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
'''

    return html


def main() -> int:
    print("🎨 Generating HTML dashboard...")

    # Load latest reports
    print("  - Loading risk score...")
    risk_score = load_latest_report("risk-score-*.json")

    print("  - Loading config drift...")
    drift = load_latest_report("config-drift-*.json")

    print("  - Loading threat intel...")
    intel = load_latest_report("threat-intel-*.json")

    print("  - Loading risk history...")
    history = load_risk_history()
    print(f"    Found: {len(history)} readings")

    # Generate HTML
    html = generate_html(risk_score, drift, intel, history)
    OUT_HTML.write_text(html, encoding="utf-8")

    print(f"\n✅ Saved: {OUT_HTML}")
    print(f"📊 Open in browser: file://{OUT_HTML}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
