#!/usr/bin/env python3
"""Static scan for risky patterns in installed skills.

Targets:
- ~/.openclaw/skills
- ~/.openclaw/extensions (optional)

Outputs:
- reports/skills-scan-<ts>.json

This is heuristic. It does NOT claim maliciousness, only flags for review.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, List

TS = time.strftime("%Y%m%d-%H%M%S")
ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)
OUT = REPORTS / f"skills-scan-{TS}.json"

SKILL_DIRS = [
    Path.home() / ".openclaw" / "skills",
    Path.home() / ".openclaw" / "extensions",
]

RISK_PATTERNS = {
    "network_exec": re.compile(r"\b(curl|wget|Invoke-WebRequest|iwr|nc\b|ncat|socat)\b", re.I),
    "shell_exec": re.compile(r"\b(os\.system|subprocess\.|exec\(|eval\(|child_process)\b", re.I),
    "persistence": re.compile(r"\b(launchctl|LaunchAgents|schtasks|systemd|crontab)\b", re.I),
    "secrets_access": re.compile(r"\b(keychain|security\s+find-|Authorization:\s*Bearer|OPENAI_API_KEY|GEMINI_API_KEY|NOTION_API_KEY)\b", re.I),
}

TEXT_EXTS = {".md", ".txt", ".js", ".ts", ".py", ".sh", ".ps1", ".json", ".yml", ".yaml"}


def scan_file(path: Path) -> Dict[str, Any]:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"path": str(path), "error": f"{type(e).__name__}: {e}"}

    hits = {}
    for name, rx in RISK_PATTERNS.items():
        m = rx.search(data)
        if m:
            # keep short context
            start = max(0, m.start() - 60)
            end = min(len(data), m.end() + 60)
            hits[name] = data[start:end].replace("\n", "\\n")
    if hits:
        return {"path": str(path), "hits": hits}
    return {}


def main() -> int:
    results: Dict[str, Any] = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "roots": [str(p) for p in SKILL_DIRS],
        "files_scanned": 0,
        "flagged": [],
        "missing_roots": [],
    }

    flagged: List[Dict[str, Any]] = []

    for root in SKILL_DIRS:
        if not root.exists():
            results["missing_roots"].append(str(root))
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in TEXT_EXTS:
                continue
            results["files_scanned"] += 1
            r = scan_file(p)
            if r.get("hits"):
                flagged.append(r)

    results["flagged"] = flagged

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT}")
    print(f"Scanned: {results['files_scanned']} files; Flagged: {len(flagged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
