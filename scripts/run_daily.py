#!/usr/bin/env python3
"""Daily guardrails job (read-only).

Runs:
- skills_scan.py
- config_extract.py
- audit.py

Designed to be used by schedulers (OpenClaw cron, systemd timer, launchd, schtasks).
Exit code is non-zero if any step fails.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    [sys.executable, str(ROOT / "scripts" / "skills_scan.py")],
    [sys.executable, str(ROOT / "scripts" / "config_extract.py")],
    [sys.executable, str(ROOT / "scripts" / "audit.py")],
]


def main() -> int:
    rc_any = 0
    for cmd in STEPS:
        p = subprocess.run(cmd)
        if p.returncode != 0:
            rc_any = p.returncode
    return rc_any


if __name__ == "__main__":
    raise SystemExit(main())
