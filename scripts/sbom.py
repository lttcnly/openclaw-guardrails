#!/usr/bin/env python3
"""SBOM-lite / provenance report for OpenClaw skills.

Collects per-skill:
- presence of SKILL.md
- origin metadata if present (e.g. .clawhub/origin.json)
- basic file inventory counts

Output:
- reports/sbom-<ts>.json
- reports/sbom.json (latest symlink/copy)
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
OUT_TS = REPORTS / f"sbom-{TS}.json"
OUT_LATEST = REPORTS / "sbom.json"

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
    sbom_data: Dict[str, Any] = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "roots": [str(p) for p in SKILL_ROOTS],
        "components": [], # Changed from 'skills' to 'components' for standardized SBOM naming
    }

    for root in SKILL_ROOTS:
        if not root.exists():
            continue
        for d in sorted([p for p in root.iterdir() if p.is_dir()]):
            component = {
                "name": d.name,
                "version": "unknown", # Try to extract version from package.json
                "root": str(root),
                "path": str(d),
                "has_skill_md": (d / "SKILL.md").exists(),
                "file_counts": {},
            }
            
            # Try to get version from package.json
            pkg_json = d / "package.json"
            if pkg_json.exists():
                data = read_json(pkg_json)
                if data and "version" in data:
                    component["version"] = data["version"]

            # count files
            total_files = 0
            exts = {}
            for p in d.rglob("*"):
                if p.is_file() and "node_modules" not in str(p):
                    total_files += 1
                    exts[p.suffix.lower()] = exts.get(p.suffix.lower(), 0) + 1
            component["file_counts"] = {"total": total_files}
            sbom_data["components"].append(component)

    content = json.dumps(sbom_data, ensure_ascii=False, indent=2)
    OUT_TS.write_text(content, encoding="utf-8")
    OUT_LATEST.write_text(content, encoding="utf-8")
    
    print(f"[✓] SBOM generated: {OUT_LATEST}")
    print(f"[*] Found {len(sbom_data['components'])} components.")
    return 0

if __name__ == "__main__":
    main()
