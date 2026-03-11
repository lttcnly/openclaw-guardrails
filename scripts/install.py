#!/usr/bin/env python3
"""Installer / bootstrap for openclaw-guardrails.

Goals:
- cross-platform
- safe by default (plan-only)
- optionally schedule periodic audits via `openclaw cron`

This script does NOT download anything. It assumes you're already inside the repo.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run(cmd: list[str]) -> int:
    p = subprocess.run(cmd)
    return p.returncode


def cron_cmds() -> list[list[str]]:
    # conservative defaults:
    # - skills scan daily at ~03:17 local time (stagger still applies unless --exact)
    # - audit weekly Monday 03:27 local time
    # - config extract daily 03:37
    return [
        ["openclaw", "cron", "add", "--name", "guardrails:skills-scan", "--cron", "17 3 * * *", "--message", "(guardrails) skills supply-chain scan", "--system-event", "guardrails:skills-scan"],
        ["openclaw", "cron", "add", "--name", "guardrails:audit", "--cron", "27 3 * * 1", "--message", "(guardrails) weekly read-only audit", "--system-event", "guardrails:audit"],
        ["openclaw", "cron", "add", "--name", "guardrails:config", "--cron", "37 3 * * *", "--message", "(guardrails) config redaction snapshot", "--system-event", "guardrails:config"],
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true", help="Print the cron plan (default)")
    ap.add_argument("--apply", action="store_true", help="Apply cron jobs (state-changing)")
    args = ap.parse_args()

    if not have("python3") and not have("python"):
        print("Python not found")
        return 1

    if not have("openclaw"):
        print("openclaw CLI not found on PATH")
        return 1

    # Always run local scripts once (read-only)
    print("[guardrails] running one-time read-only checks...")
    run([sys.executable, str(ROOT / "scripts" / "skills_scan.py")])
    run([sys.executable, str(ROOT / "scripts" / "config_extract.py")])
    run([sys.executable, str(ROOT / "scripts" / "audit.py")])

    cmds = cron_cmds()

    print("\n[guardrails] cron plan (optional):")
    for c in cmds:
        print("  ", " ".join(c))

    if not args.apply:
        print("\n(no changes applied; re-run with --apply to create cron jobs)")
        return 0

    # Apply (explicit)
    print("\n[guardrails] APPLY MODE: creating cron jobs")
    for c in cmds:
        rc = run(c)
        if rc != 0:
            print("failed:", " ".join(c))
            return rc

    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
