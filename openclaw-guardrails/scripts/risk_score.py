#!/usr/bin/env python3
"""Calculate risk score (0-100) using meta.json and guardrails.yaml.
"""

from __future__ import annotations

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
LOGS = ROOT / "logs"
CONFIG_FILE = ROOT / "guardrails.yaml"
META_FILE = REPORTS / "meta.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOGS / "guardrails.log"), logging.StreamHandler()]
)
logger = logging.getLogger("risk_score")

TS = time.strftime("%Y%m%d-%H%M%S")
SCORE_OUT = REPORTS / f"risk-score-{TS}.json"
SUMMARY_OUT = REPORTS / f"summary-{TS}.md"

def load_config() -> Dict:
    try:
        import yaml
        if CONFIG_FILE.exists():
            return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"Could not load yaml config, using defaults: {e}")
    
    return {
        "scoring": {"audit_weight": 0.5, "skills_weight": 0.2, "threat_intel_weight": 0.2, "drift_weight": 0.1},
        "thresholds": {"critical": 40, "high": 60, "medium": 80}
    }

def load_latest_report(report_type: str) -> Dict | None:
    if not META_FILE.exists(): return None
    try:
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))
        report_path = meta.get(report_type, {}).get("latest")
        if report_path and Path(report_path).exists():
            return json.loads(Path(report_path).read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load latest {report_type} report: {e}")
    return None

def calc_score(config: Dict) -> Dict[str, Any]:
    score = 100.0
    weights = config.get("scoring", {})
    breakdown = []

    # 1. Audit
    audit = load_latest_report("security_audit") # OpenClaw native audit
    if audit:
        crit = int(audit.get("summary", {}).get("critical", 0))
        warn = int(audit.get("summary", {}).get("warn", 0))
        deduction = (crit * 20 + warn * 5) * weights.get("audit_weight", 0.5)
        score -= deduction
        breakdown.append({"category": "Security Audit", "deduction": round(deduction, 1)})

    # 2. Threat Intel
    intel = load_latest_report("threat_intel")
    if intel:
        summary = intel.get("summary", {})
        crit = summary.get("critical", 0)
        high = summary.get("high", 0)
        deduction = (crit * 15 + high * 8) * weights.get("threat_intel_weight", 0.2)
        score -= deduction
        breakdown.append({"category": "Threat Intel", "deduction": round(deduction, 1)})

    # 3. Skills Scan
    skills = load_latest_report("skills_scan")
    if skills:
        flagged = len(skills.get("flagged", []))
        deduction = (flagged * 10) * weights.get("skills_weight", 0.2)
        score -= deduction
        breakdown.append({"category": "Skills Supply-Chain", "deduction": round(deduction, 1)})

    score = max(0.0, min(100.0, score))
    
    # Determine Level
    thresh = config.get("thresholds", {})
    if score < thresh.get("critical", 40): level, color = "CRITICAL", "🔴"
    elif score < thresh.get("high", 60): level, color = "HIGH", "🟠"
    elif score < thresh.get("medium", 80): level, color = "MEDIUM", "🟡"
    else: level, color = "LOW", "🟢"

    return {
        "timestamp": datetime.now().isoformat(),
        "score": round(score, 1),
        "level": level,
        "color": color,
        "breakdown": breakdown
    }

from datetime import datetime
def main() -> int:
    config = load_config()
    score_data = calc_score(config)
    
    SCORE_OUT.write_text(json.dumps(score_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Update meta.json
    meta = {}
    if META_FILE.exists(): meta = json.loads(META_FILE.read_text())
    meta["risk_score"] = {"latest": str(SCORE_OUT), "timestamp": score_data["timestamp"], "status": "success"}
    META_FILE.write_text(json.dumps(meta, indent=2))
    
    logger.info(f"Risk Score: {score_data['score']} ({score_data['level']})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
