#!/usr/bin/env python3
"""Auto-Remediation: Automatically fix low-risk security issues.

Auto-fix categories (no confirmation required):
- Dependency upgrades (npm update, pip install --upgrade)
- Config restoration to secure baseline (groupPolicy, etc.)

Outputs:
- reports/auto-fix-<ts>.json
- backups/ (before any modification)
- updates reports/meta.json
"""

from __future__ import annotations

import json
import subprocess
import time
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
LOGS = ROOT / "logs"
BACKUPS = ROOT / "backups"
REPORTS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "guardrails.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("auto_fix")

TS = time.strftime("%Y%m%d-%H%M%S")
OUT_JSON = REPORTS / f"auto-fix-{TS}.json"
META_FILE = REPORTS / "meta.json"

AUTO_FIX_CONFIG = {
    "groupPolicy": {"unsafe": "open", "safe": "allowlist"},
    "tools.fs.workspaceOnly": {"unsafe": False, "safe": True},
}

def update_meta(report_type: str, file_path: Path):
    meta = {}
    if META_FILE.exists():
        try:
            meta = json.loads(META_FILE.read_text(encoding="utf-8"))
        except: pass
    meta[report_type] = {"latest": str(file_path), "timestamp": time.time(), "status": "success"}
    META_FILE.write_text(json.dumps(meta, indent=2), encoding="utf-8")

def backup_file(path: Path) -> Path | None:
    if not path.exists(): return None
    ts = time.strftime("%Y%m%d-%H%M%S")
    dst = BACKUPS / f"{path.name}.{ts}.bak"
    try:
        shutil.copy2(path, dst)
        logger.info(f"Backup created: {dst}")
        return dst
    except Exception as e:
        logger.error(f"Backup failed for {path}: {e}")
        return None

def run_safe_cmd(cmd: List[str], cwd: str | None = None) -> subprocess.CompletedProcess | None:
    """Run subprocess safely using list arguments."""
    try:
        logger.info(f"Executing: {' '.join(cmd)}")
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=cwd)
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        return None

def fix_config(execute: bool = False) -> List[Dict]:
    results = []
    # Try to locate openclaw.json
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if not config_path.exists(): return results
    
    try:
        content = json.loads(config_path.read_text(encoding="utf-8"))
        modified = False
        
        # Simple depth-1 traversal for config (extend if needed)
        # This is a simplified example; actual config paths are deep
        # For now, we use the 'openclaw config set' CLI as it handles deep keys better
        
        # Example: Check discord groupPolicy
        # In openclaw.json: channels.discord.groupPolicy
        discord_policy = content.get("channels", {}).get("discord", {}).get("groupPolicy")
        if discord_policy == "open":
            cmd = ["openclaw", "config", "set", "channels.discord.groupPolicy=allowlist"]
            if execute:
                backup_file(config_path)
                res = run_safe_cmd(cmd)
                status = "executed" if res and res.returncode == 0 else "failed"
            else:
                status = "simulated"
            results.append({"path": "channels.discord.groupPolicy", "action": "set allowlist", "status": status})

    except Exception as e:
        logger.error(f"Config fix logic failed: {e}")
    
    return results

def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()

    logger.info(f"Starting auto-fix (execute={args.execute})")
    
    config_results = fix_config(execute=args.execute)
    
    report = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "execute_mode": args.execute,
        "results": config_results
    }
    
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    update_meta("auto_fix", OUT_JSON)
    
    logger.info("Auto-fix process completed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
