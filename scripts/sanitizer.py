#!/usr/bin/env python3
"""Sanitizer: Identifies and redacts PII/Credentials in project files and logs.
Can be integrated into the audit flow to ensure no secrets are leaked.
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
REPORTS = ROOT / "reports"
LOGS.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

# Common patterns for secrets and PII
PATTERNS = {
    "API_KEY": r"(?:api[_-]?key|secret|token|password)[\s:=]+[\"']?([a-zA-Z0-9_\-\.]{16,})[\"']?",
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "IP_ADDR": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "JWT_TOKEN": r"ey[a-zA-Z0-9_-]+\.ey[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
}

def sanitize_text(text: str) -> str:
    """Replaces sensitive patterns with [REDACTED]."""
    for name, pattern in PATTERNS.items():
        text = re.sub(pattern, f"<{name}:REDACTED>", text, flags=re.IGNORECASE)
    return text

def scan_file(file_path: Path) -> List[Dict]:
    """Scans a file for sensitive info."""
    findings = []
    if not file_path.is_file() or file_path.suffix in ['.png', '.jpg', '.exe', '.pyc']:
        return findings
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "type": name,
                    "file": str(file_path),
                    "line": content.count('\n', 0, match.start()) + 1,
                    "match": match.group(0)[:10] + "..." # Redacted preview
                })
    except Exception as e:
        pass
    return findings

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(Path.home() / ".openclaw"))
    args = ap.parse_args()

    target_dir = Path(args.dir)
    all_findings = []
    print(f"[*] Scanning for sensitive information in {target_dir}...")

    # Focus on config and logs
    for ext in ['*.json', '*.log', '*.yaml', '*.yml', '.env']:
        for file in target_dir.rglob(ext):
            if "node_modules" in str(file) or "venv" in str(file):
                continue
            all_findings.extend(scan_file(file))

    out_file = REPORTS / "sanitization-report.json"
    with open(out_file, 'w') as f:
        json.dump(all_findings, f, indent=2)
    
    print(f"[✓] Sanitization scan complete. Found {len(all_findings)} items. Report: {out_file}")

if __name__ == "__main__":
    main()
