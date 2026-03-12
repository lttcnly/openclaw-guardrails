#!/usr/bin/env python3
"""SBOM-lite / provenance report for OpenClaw skills.

Collects per-skill:
- presence of SKILL.md
- origin metadata if present (e.g. .clawhub/origin.json)
- basic file inventory counts

Output:
- reports/sbom-<ts>.json
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
OUT = REPORTS / f"sbom-{TS}.json"

SKILL_ROOTS = [
    Path.home() / ".openclaw" / "skills",
    Path.home() / ".openclaw" / "extensions",
]


def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    sbom: Dict[str, Any] = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "roots": [str(p) for p in SKILL_ROOTS],
        "skills": [],
    }

    for root in SKILL_ROOTS:
        if not root.exists():
            continue
        for d in sorted([p for p in root.iterdir() if p.is_dir()]):
            skill = {
                "name": d.name,
                "root": str(root),
                "path": str(d),
                "has_skill_md": (d / "SKILL.md").exists(),
                "origin": None,
                "file_counts": {},
            }
            origin = d / ".clawhub" / "origin.json"
            if origin.exists():
                skill["origin"] = read_json(origin)

            # count files
            total_files = 0
            exts = {}
            for p in d.rglob("*"):
                if p.is_file():
                    total_files += 1
                    exts[p.suffix.lower()] = exts.get(p.suffix.lower(), 0) + 1
            skill["file_counts"] = {"total": total_files, "exts_top": sorted(exts.items(), key=lambda x: x[1], reverse=True)[:20]}
            sbom["skills"].append(skill)

    OUT.write_text(json.dumps(sbom, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT}")
    print(f"Skills: {len(sbom['skills'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
