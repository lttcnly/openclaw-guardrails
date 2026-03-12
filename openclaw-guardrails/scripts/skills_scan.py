#!/usr/bin/env python3
"""Static scan for risky patterns in installed OpenClaw skills.

Goal: quickly triage supply-chain risk.

This is heuristic. It does NOT prove maliciousness.

Targets:
- ~/.openclaw/skills
- ~/.openclaw/extensions (optional)

Outputs:
- reports/skills-scan-<ts>.json (structured)
- reports/skills-scan-<ts>.md  (human summary)

Severity rules (rough):
- HIGH: (secrets_access + network_exec) in code-like file, or persistence + shell_exec in code
- MED:  2+ hit-types in code-like file
- LOW:  hits in docs/examples (md/txt) or single hit-type
"""

from __future__ import annotations

import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Any, List, Tuple

TS = time.strftime("%Y%m%d-%H%M%S")
ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)
OUT_JSON = REPORTS / f"skills-scan-{TS}.json"
OUT_MD = REPORTS / f"skills-scan-{TS}.md"

SKILL_DIRS = [
    Path.home() / ".openclaw" / "skills",
    Path.home() / ".openclaw" / "extensions",
]

RISK_PATTERNS = {
    "network_exec": re.compile(r"\b(curl\b|wget\b|Invoke-WebRequest|\biwr\b|\bnc\b|ncat|socat)\b", re.I),
    "shell_exec": re.compile(r"\b(os\.system\b|subprocess\.|exec\(|eval\(|child_process)\b", re.I),
    "persistence": re.compile(r"\b(launchctl|LaunchAgents|schtasks|systemd|crontab)\b", re.I),
    "secrets_access": re.compile(r"\b(keychain|security\s+find-|Authorization:\s*Bearer|OPENAI_API_KEY|GEMINI_API_KEY|NOTION_API_KEY)\b", re.I),
}

DOC_EXTS = {".md", ".txt"}
CODE_EXTS = {".js", ".ts", ".py", ".sh", ".ps1", ".json", ".yml", ".yaml"}
TEXT_EXTS = DOC_EXTS | CODE_EXTS


def skill_root(path: Path) -> str:
    # Try to infer skill folder name under ~/.openclaw/skills/<name>/...
    parts = path.parts
    for i, p in enumerate(parts):
        if p == "skills" and i + 1 < len(parts):
            return parts[i + 1]
        if p == "extensions" and i + 1 < len(parts):
            return parts[i + 1]
    return "<unknown>"


def is_docs_file(path: Path) -> bool:
    if path.suffix.lower() in DOC_EXTS:
        return True
    # treat typical docs dirs as docs
    lowered = "/".join(path.parts).lower()
    return any(seg in lowered for seg in ["/docs/", "/examples/", "/references/"])


def scan_file(path: Path) -> Dict[str, Any]:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"path": str(path), "error": f"{type(e).__name__}: {e}"}

    hits: Dict[str, str] = {}
    for name, rx in RISK_PATTERNS.items():
        m = rx.search(data)
        if m:
            start = max(0, m.start() - 60)
            end = min(len(data), m.end() + 60)
            hits[name] = data[start:end].replace("\n", "\\n")

    if not hits:
        return {}

    hit_types = set(hits.keys())
    docs = is_docs_file(path)

    # severity heuristic
    severity = "LOW"
    if not docs:
        if ("secrets_access" in hit_types and "network_exec" in hit_types) or (
            "persistence" in hit_types and "shell_exec" in hit_types
        ):
            severity = "HIGH"
        elif len(hit_types) >= 2:
            severity = "MED"
        else:
            severity = "LOW"
    else:
        severity = "LOW"

    return {
        "path": str(path),
        "skill": skill_root(path),
        "severity": severity,
        "docs": docs,
        "hits": hits,
    }


def main() -> int:
    results: Dict[str, Any] = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "roots": [str(p) for p in SKILL_DIRS],
        "files_scanned": 0,
        "flagged": [],
        "missing_roots": [],
        "summary": {},
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

    # Summaries
    sev = Counter([x.get("severity") for x in flagged])
    by_type = Counter()
    by_skill = defaultdict(lambda: Counter())
    for item in flagged:
        for t in item.get("hits", {}).keys():
            by_type[t] += 1
        by_skill[item.get("skill", "<unknown>")][item.get("severity", "LOW")] += 1

    results["flagged"] = flagged
    results["summary"] = {
        "flagged_total": len(flagged),
        "severity": dict(sev),
        "hit_types": dict(by_type),
        "skills_top": sorted(
            ((k, sum(v.values()), dict(v)) for k, v in by_skill.items()),
            key=lambda x: x[1],
            reverse=True,
        )[:30],
    }

    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # Human summary
    lines = []
    lines.append(f"# Skills Supply-Chain Scan ({results['time']})")
    lines.append("")
    lines.append(f"Scanned files: {results['files_scanned']}")
    lines.append(f"Flagged: {len(flagged)}")
    lines.append("")
    lines.append("## Severity")
    for k in ("HIGH", "MED", "LOW"):
        lines.append(f"- {k}: {sev.get(k, 0)}")
    lines.append("")
    lines.append("## Hit types")
    for k, v in by_type.most_common():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Top skills (flagged)")
    for skill, total, dist in results["summary"]["skills_top"]:
        lines.append(f"- {skill}: {total} (H:{dist.get('HIGH',0)} M:{dist.get('MED',0)} L:{dist.get('LOW',0)})")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Saved: {OUT_JSON}")
    print(f"Saved: {OUT_MD}")
    print(f"Scanned: {results['files_scanned']} files; Flagged: {len(flagged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
