#!/usr/bin/env python3
"""Silent guardrails enforcement (state-changing).

Edits ~/.openclaw/openclaw.json to reduce exposure when critical findings exist.

Design:
- Always writes a timestamped backup under reports/backups/
- Writes a change log under reports/enforce-<ts>.json
- Best-effort restart of OpenClaw gateway to apply changes

What it enforces (minimal, high impact):
1) channels.*.groupPolicy: open -> allowlist
2) plugins.entries.feishu-openclaw-plugin.enabled: true -> false (quarantine)

This is intentionally conservative: it does NOT touch host firewall, SSH, or OS settings.
"""

from __future__ import annotations

import argparse
import json
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple
import subprocess

HOME = Path.home()
CFG = HOME / ".openclaw" / "openclaw.json"
ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
BACKUPS = REPORTS / "backups"
REPORTS.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")


def deep_get(d: Any, path: List[str]) -> Any:
    cur = d
    for k in path:
        if isinstance(cur, dict):
            cur = cur.get(k)
        else:
            return None
    return cur


def deep_set(d: Dict[str, Any], path: List[str], value: Any) -> Tuple[bool, Any, Any]:
    cur: Any = d
    for k in path[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    last = path[-1]
    old = cur.get(last)
    if old == value:
        return False, old, value
    cur[last] = value
    return True, old, value


def enforce(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    changes: List[Dict[str, Any]] = []

    # 1) groupPolicy open -> allowlist
    group_paths: List[Tuple[List[str], Any]] = []

    def walk(obj: Any, prefix: List[str]):
        if isinstance(obj, dict):
            for k, v in obj.items():
                p = prefix + [k]
                if k == "groupPolicy":
                    group_paths.append((p, v))
                walk(v, p)

    walk(cfg, [])

    for p, v in group_paths:
        if v == "open":
            changed, old, new = deep_set(cfg, p, "allowlist")
            if changed:
                changes.append({"path": ".".join(p), "old": old, "new": new, "reason": "reduce open-group prompt-injection risk"})

    # 2) quarantine feishu-openclaw-plugin
    p = ["plugins", "entries", "feishu-openclaw-plugin", "enabled"]
    cur = deep_get(cfg, p)
    if cur is True:
        changed, old, new = deep_set(cfg, p, False)
        if changed:
            changes.append({"path": ".".join(p), "old": old, "new": new, "reason": "plugin flagged by openclaw security audit (code safety)"})

    return changes


def restart_gateway() -> Tuple[int, str, str]:
    try:
        p = subprocess.run(["openclaw", "gateway", "restart"], capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 999, "", f"{type(e).__name__}: {e}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Apply changes")
    ap.add_argument("--plan", action="store_true", help="Print plan only")
    ap.add_argument("--notify", action="store_true", default=True, help="Push a system event to OpenClaw main session (default: true)")
    ap.add_argument("--no-notify", action="store_true", help="Disable system event notification")
    ap.add_argument("--notify-mode", default="next-heartbeat", help="openclaw system event mode: now|next-heartbeat")
    args = ap.parse_args()

    if args.no_notify:
        args.notify = False

    if not CFG.exists():
        print(f"missing config: {CFG}")
        return 1

    raw = json.loads(CFG.read_text(encoding="utf-8"))
    planned = deepcopy(raw)
    changes = enforce(planned)

    plan_out = REPORTS / f"enforce-plan-{TS}.json"
    plan_out.write_text(json.dumps({"time": TS, "changes": changes}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved plan: {plan_out}")

    if not changes:
        print("No changes needed")
        return 0

    if not args.apply:
        print("(not applied; re-run with --apply)")
        return 0

    # backup
    backup = BACKUPS / f"openclaw.json.{TS}.bak"
    backup.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    # write new
    CFG.write_text(json.dumps(planned, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # restart
    rc, out, err = restart_gateway()

    log = {
        "time": TS,
        "backup": str(backup),
        "config": str(CFG),
        "changes": changes,
        "gateway_restart": {"rc": rc, "stdout": out[-4000:], "stderr": err[-4000:]},
    }
    outp = REPORTS / f"enforce-applied-{TS}.json"
    outp.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Applied. Saved: {outp}")

    # Notify OpenClaw main session (best-effort, silent if fails)
    if args.notify:
        try:
            lines = ["[guardrails] 拦截已执行（自动降权）"]
            lines.append(f"- backup: {backup}")
            lines.append(f"- log: {outp}")
            for c in changes[:20]:
                lines.append(f"- {c['path']}: {c['old']} -> {c['new']}")
            text = "\n".join(lines)
            subprocess.run([
                "openclaw", "system", "event",
                "--mode", str(args.notify_mode),
                "--text", text,
            ], timeout=30)
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
