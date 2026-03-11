#!/usr/bin/env python3
"""Extract a redacted OpenClaw config summary (read-only).

Reads ~/.openclaw/openclaw.json and writes a redacted summary to reports/.
Does NOT print raw secrets.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict

TS = time.strftime("%Y%m%d-%H%M%S")
ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)
OUT = REPORTS / f"openclaw-config-redacted-{TS}.json"

CFG = Path.home() / ".openclaw" / "openclaw.json"

REDACT_KEYS = re.compile(r"(token|secret|api[_-]?key|authorization|bearer|password)", re.I)


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(k, str) and REDACT_KEYS.search(k):
                out[k] = "<redacted>"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    if isinstance(obj, str):
        if re.search(r"\b(sk-|Bearer\s+)[A-Za-z0-9_.-]{8,}", obj):
            return "<redacted>"
        return obj
    return obj


def pick(d: Dict[str, Any], *keys: str) -> Dict[str, Any]:
    return {k: d.get(k) for k in keys if k in d}


def main() -> int:
    if not CFG.exists():
        print(f"missing: {CFG}")
        return 1

    raw = json.loads(CFG.read_text(encoding="utf-8"))

    # Keep only the most security-relevant top-level sections.
    summary: Dict[str, Any] = {
        "gateway": raw.get("gateway"),
        "browser": raw.get("browser"),
        "canvasHost": raw.get("canvasHost"),
        "security": raw.get("security"),
        "tools": raw.get("tools"),
        "plugins": raw.get("plugins"),
        "channels": raw.get("channels"),
        "agents": raw.get("agents"),
        "devices": raw.get("devices"),
    }

    OUT.write_text(json.dumps(redact(summary), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
