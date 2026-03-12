#!/usr/bin/env python3
"""Cross-platform OpenClaw + host posture audit (read-only).

Writes reports under ./reports/.
- audit-<ts>.txt: human readable
- audit-<ts>.json: structured summary

Design goals:
- macOS/Linux/Windows support
- tolerate missing commands
- never prints secrets intentionally

NOTE: It still calls `openclaw` which may print config paths; we avoid dumping raw config.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
TXT_PATH = REPORTS / f"audit-{TS}.txt"
JSON_PATH = REPORTS / f"audit-{TS}.json"

REDACT_KEYS = re.compile(r"(token|secret|api[_-]?key|authorization|bearer|password)", re.I)


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run(cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 999, "", f"{type(e).__name__}: {e}"


def peel_json(mixed: str) -> Optional[dict]:
    """OpenClaw CLI sometimes prints logs before JSON. Extract from first '{'."""
    i = mixed.find('{')
    if i < 0:
        return None
    try:
        return json.loads(mixed[i:])
    except Exception:
        return None


def redact_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(k, str) and REDACT_KEYS.search(k):
                out[k] = "<redacted>"
            else:
                out[k] = redact_obj(v)
        return out
    if isinstance(obj, list):
        return [redact_obj(x) for x in obj]
    if isinstance(obj, str):
        # redact obvious bearer strings
        if re.search(r"\b(sk-|Bearer\s+)[A-Za-z0-9_.-]{8,}", obj):
            return "<redacted>"
        return obj
    return obj


def os_listeners() -> str:
    sysname = platform.system()
    if sysname == "Darwin":
        cmd = ["/usr/sbin/netstat", "-anv", "-p", "tcp"]
        rc, out, err = run(cmd, timeout=20)
        if rc == 0:
            lines = [ln for ln in out.splitlines() if "LISTEN" in ln]
            return "\n".join(lines)
        return err or out
    if sysname == "Linux":
        if have("ss"):
            rc, out, err = run(["ss", "-ltnp"], timeout=20)
            return out if rc == 0 else (err or out)
        if have("netstat"):
            rc, out, err = run(["netstat", "-tulpn"], timeout=20)
            return out if rc == 0 else (err or out)
        return "no ss/netstat"
    if sysname == "Windows":
        rc, out, err = run(["cmd", "/c", "netstat -ano"], timeout=20)
        if rc == 0:
            lines = [ln for ln in out.splitlines() if "LISTEN" in ln.upper()]
            return "\n".join(lines[:400])
        return err or out
    return f"unsupported system: {sysname}"


def firewall_status() -> str:
    sysname = platform.system()
    if sysname == "Darwin":
        rc, out, err = run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"], timeout=10)
        return out.strip() if rc == 0 else (err.strip() or out.strip())
    if sysname == "Linux":
        if have("ufw"):
            rc, out, err = run(["ufw", "status"], timeout=10)
            return out.strip() if rc == 0 else (err.strip() or out.strip())
        if have("firewall-cmd"):
            rc, out, err = run(["firewall-cmd", "--state"], timeout=10)
            return out.strip() if rc == 0 else (err.strip() or out.strip())
        if have("nft"):
            rc, out, err = run(["nft", "list", "ruleset"], timeout=10)
            return out[:4000] if rc == 0 else (err.strip() or out.strip())
        return "no ufw/firewalld/nft"
    if sysname == "Windows":
        rc, out, err = run(["cmd", "/c", "netsh advfirewall show allprofiles"], timeout=20)
        return out.strip() if rc == 0 else (err.strip() or out.strip())
    return f"unsupported system: {sysname}"


def openclaw_cmd(args: List[str], timeout: int = 60) -> Dict[str, Any]:
    cmd = ["openclaw"] + args
    rc, out, err = run(cmd, timeout=timeout)
    return {"cmd": " ".join(cmd), "rc": rc, "stdout": out, "stderr": err}


def main() -> int:
    summary: Dict[str, Any] = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "openclaw": {},
        "host": {},
    }

    lines: List[str] = []
    def emit(s: str = ""):
        lines.append(s)

    emit("== OpenClaw Guardrails Audit (read-only, cross-platform) ==")
    emit(f"time: {summary['time']}")
    emit(f"platform: {summary['platform']}")
    emit()

    # openclaw section
    for name, args, to in [
        ("openclaw --version", ["--version"], 15),
        ("openclaw status", ["status"], 30),
        ("openclaw gateway status", ["gateway", "status"], 30),
        ("openclaw security audit --deep", ["security", "audit", "--deep"], 60),
        ("openclaw update status", ["update", "status"], 30),
        ("openclaw skills check", ["skills", "check"], 30),
        ("openclaw models status --probe --json", ["models", "status", "--probe", "--json"], 60),
    ]:
        emit(f"-- {name}")
        res = openclaw_cmd(args, timeout=to)
        emit((res["stdout"] or res["stderr"] or "").strip())
        emit()
        summary["openclaw"][name] = {k: res[k] for k in ("cmd", "rc")}
        if name.endswith("--json"):
            data = peel_json(res["stdout"] + "\n" + res["stderr"])
            if data:
                summary["openclaw"]["models_status"] = redact_obj(data)

    # host section
    emit("-- firewall status")
    fw = firewall_status()
    emit(fw)
    emit()

    emit("-- listening ports")
    lst = os_listeners()
    emit(lst)
    emit()

    summary["host"]["firewall"] = fw
    # avoid huge netstat on windows; store first 4k
    summary["host"]["listeners"] = lst[:4000]

    TXT_PATH.write_text("\n".join(lines), encoding="utf-8")
    JSON_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved: {TXT_PATH}")
    print(f"Saved: {JSON_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
