#!/usr/bin/env python3
"""Threat Intel: Real-time identification of risky patterns.
Focus: Identifying risky Tool Calls (Financial, System-level).
"""

import json
import re
from pathlib import Path
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

RISKY_TOOL_PATTERNS = {
    "FINANCIAL": [r"transfer", r"pay", r"wallet", r"withdraw", r"deposit", r"blockchain"],
    "DESTRUCTIVE": [r"rm\s+-rf", r"chmod\s+777", r"chown", r"format", r"mkfs"],
    "EXFILTRATION": [r"curl.*upload", r"scp", r"nc\s+-e", r"bash\s+-i"],
}

def analyze_intent(text: str) -> List[Dict]:
    """Analyzes a snippet of text for risky intents."""
    findings = []
    for category, patterns in RISKY_TOOL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append({
                    "category": category,
                    "pattern": pattern,
                    "severity": "CRITICAL" if category in ["FINANCIAL", "DESTRUCTIVE"] else "HIGH"
                })
    return findings

def scan_logs_for_intent() -> List[Dict]:
    """Scans OpenClaw logs for suspicious agent intents."""
    log_dir = Path.home() / ".openclaw" / "logs"
    findings = []
    if not log_dir.exists(): return findings

    for log_file in log_dir.glob("*.log"):
        try:
            with open(log_file, 'r') as f:
                # Read last 1000 lines for efficiency
                lines = f.readlines()[-1000:]
                for i, line in enumerate(lines):
                    intent_results = analyze_intent(line)
                    for r in intent_results:
                        findings.append({
                            "log": str(log_file),
                            "line": i + 1,
                            "category": r["category"],
                            "match": r["pattern"],
                            "severity": r["severity"]
                        })
        except: pass
    return findings

def main():
    print("[*] Running Threat Intel: Analyzing tool-call intent and OS commands...")
    log_findings = scan_logs_for_intent()
    
    out_file = REPORTS / "threat-intel-report.json"
    with open(out_file, 'w') as f:
        json.dump(log_findings, f, indent=2)
    
    print(f"[✓] Threat Intel complete. Identified {len(log_findings)} risky intents. Report: {out_file}")

if __name__ == "__main__":
    main()
