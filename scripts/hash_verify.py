#!/usr/bin/env python3
"""Verify current skill hashes against a baseline manifest.

Usage:
  python3 scripts/hash_verify.py --baseline reports/skill-hashes-<ts>.json

Exit codes:
- 0: OK
- 2: Differences found
- 1: Error
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, Any

MAX_FILE_BYTES = 5 * 1024 * 1024


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    args = ap.parse_args()

    baseline_path = Path(args.baseline)
    if not baseline_path.exists():
        print(f"missing baseline: {baseline_path}")
        return 1

    base: Dict[str, Any] = json.loads(baseline_path.read_text(encoding="utf-8"))
    roots = [Path(p).expanduser() for p in base.get("roots", [])]

    diffs = []

    for skill, info in base.get("skills", {}).items():
        root = Path(info.get("root", roots[0] if roots else Path.home()/".openclaw"/"skills"))
        for f in info.get("files", []):
            rel = f["path"]
            expected = f["sha256"]
            p = root / rel
            if not p.exists():
                diffs.append({"skill": skill, "path": str(p), "type": "missing"})
                continue
            st = p.stat()
            if st.st_size > MAX_FILE_BYTES:
                continue
            actual = sha256_file(p)
            if actual != expected:
                diffs.append({"skill": skill, "path": str(p), "type": "changed", "expected": expected, "actual": actual})

    if diffs:
        print("DIFFS FOUND:")
        for d in diffs[:200]:
            print(f"- {d['type']} {d['path']}")
        print(f"Total diffs: {len(diffs)}")
        return 2

    print("OK: baseline matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
