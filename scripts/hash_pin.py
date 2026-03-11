#!/usr/bin/env python3
"""Generate a baseline hash manifest for OpenClaw skills.

Purpose: detect unexpected changes (supply-chain tampering, silent updates).

Default roots:
- ~/.openclaw/skills
- ~/.openclaw/extensions

Output:
- reports/skill-hashes-<ts>.json

Notes:
- Read-only.
- Skips very large files by default (to keep runtime reasonable).
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
OUT = REPORTS / f"skill-hashes-{TS}.json"

DEFAULT_ROOTS = [
    Path.home() / ".openclaw" / "skills",
    Path.home() / ".openclaw" / "extensions",
]

MAX_FILE_BYTES = 5 * 1024 * 1024  # 5MB


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def skill_name(root: Path, file_path: Path) -> str:
    try:
        rel = file_path.relative_to(root)
    except Exception:
        return "<unknown>"
    parts = rel.parts
    return parts[0] if parts else "<unknown>"


def main() -> int:
    manifest: Dict[str, Any] = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "roots": [str(p) for p in DEFAULT_ROOTS],
        "max_file_bytes": MAX_FILE_BYTES,
        "skills": {},
    }

    for root in DEFAULT_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            try:
                st = p.stat()
            except Exception:
                continue
            if st.st_size > MAX_FILE_BYTES:
                continue

            name = skill_name(root, p)
            entry = manifest["skills"].setdefault(name, {"files": [], "root": str(root)})
            rel = str(p.relative_to(root))
            entry["files"].append({
                "path": rel,
                "bytes": st.st_size,
                "sha256": sha256_file(p),
            })

    # stable ordering
    for name in list(manifest["skills"].keys()):
        manifest["skills"][name]["files"] = sorted(manifest["skills"][name]["files"], key=lambda x: x["path"])

    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT}")
    print(f"Skills: {len(manifest['skills'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
