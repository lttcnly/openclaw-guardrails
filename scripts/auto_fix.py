#!/usr/bin/env python3
"""Auto-Remediation: Automatically fix low-risk security issues.

Auto-fix categories:
- Configuration baseline enforcement (authMode, systemRunApproval, etc.)
- Restoration of unsafe groupPolicy settings
- Backup before any modification

Outputs:
- reports/auto-fix-<ts>.json
- backups/ (timestamped snapshots)
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

# --- Security Baseline Definition ---
# These paths correspond to nested keys in openclaw.json
SECURITY_BASELINE = {
    "authMode": "token",
    "systemRunApproval": "always",
    "allowInsecure": False,
    "groupPolicy": "allowlist"  # Default fallback
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
    try:
        logger.info(f"Executing: {' '.join(cmd)}")
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=cwd)
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        return None

def get_nested(data, path_str, default=None):
    """Safely get a nested value using dot notation."""
    keys = path_str.split('.')
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data

def set_nested(data, path_str, value):
    """Safely set a nested value using dot notation."""
    keys = path_str.split('.')
    for key in keys[:-1]:
        data = data.setdefault(key, {})
    data[keys[-1]] = value

def enforce_baseline(content: Dict, execute: bool = False) -> List[Dict]:
    """Check and fix openclaw.json against the security baseline."""
    results = []
    modified = False

    # Check top-level security fields
    for key, expected in SECURITY_BASELINE.items():
        actual = content.get(key)
        if actual != expected:
            results.append({
                "path": key,
                "expected": str(expected),
                "actual": str(actual),
                "severity": "CRITICAL",
                "action": f"Revert to {expected}",
                "status": "pending"
            })
            if execute:
                content[key] = expected
                modified = True
                results[-1]["status"] = "fixed"

    # Check all channels for groupPolicy="open"
    channels = content.get("channels", {})
    for channel_name, channel_cfg in channels.items():
        if isinstance(channel_cfg, dict) and channel_cfg.get("groupPolicy") == "open":
            path = f"channels.{channel_name}.groupPolicy"
            results.append({
                "path": path,
                "expected": "allowlist",
                "actual": "open",
                "severity": "HIGH",
                "action": "Set to allowlist",
                "status": "pending"
            })
            if execute:
                channel_cfg["groupPolicy"] = "allowlist"
                modified = True
                results[-1]["status"] = "fixed"

    return results, modified

def fix_config(execute: bool = False) -> List[Dict]:
    all_results = []
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if not config_path.exists():
        logger.warning(f"Config not found at {config_path}")
        return all_results
    
    try:
        content = json.loads(config_path.read_text(encoding="utf-8"))
        baseline_results, modified = enforce_baseline(content, execute)
        all_results.extend(baseline_results)

        if modified and execute:
            backup_file(config_path)
            config_path.write_text(json.dumps(content, indent=2), encoding="utf-8")
            logger.info(f"Security baseline enforced and saved to {config_path}")

    except Exception as e:
        logger.error(f"Config remediation failed: {e}")
    
    return all_results

def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="Apply fixes instead of just dry-run")
    args = ap.parse_args()

    logger.info(f"Starting auto-remediation (execute={args.execute})")
    
    results = fix_config(execute=args.execute)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "execute_mode": args.execute,
        "summary": {
            "total_issues": len(results),
            "fixed": sum(1 for r in results if r["status"] == "fixed"),
            "pending": sum(1 for r in results if r["status"] == "pending")
        },
        "details": results
    }
    
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    update_meta("auto_fix", OUT_JSON)
    
    logger.info(f"Auto-fix process completed. Found {len(results)} issues.")
    return 0

if __name__ == "__main__":
    main()
