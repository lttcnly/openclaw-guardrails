#!/usr/bin/env python3
"""Daily guardrails job with Parallel Execution and Centralized Logging.
"""

from __future__ import annotations

import subprocess
import sys
import time
import logging
import json
import concurrent.futures
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
REPORTS = ROOT / "reports"
SCRIPTS = ROOT / "scripts"
LOGS.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOGS / "guardrails.log"), logging.StreamHandler()]
)
logger = logging.getLogger("daily_run")

def run_script(script_name: str, args: list = []) -> bool:
    script_path = SCRIPTS / script_name
    if not script_path.exists():
        logger.error(f"Script not found: {script_name}")
        return False
    
    logger.info(f"Starting: {script_name}")
    try:
        cmd = [sys.executable, str(script_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logger.info(f"Success: {script_name}")
            return True
        else:
            logger.error(f"Failed: {script_name} (Code {result.returncode})")
            logger.error(f"Stderr: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"Exception running {script_name}: {e}")
        return False

def main() -> int:
    start_time = time.time()
    logger.info("=== OpenClaw Guardrails Daily Run Started ===")

    # 1. Sequential Prep Tasks
    run_script("config_extract.py")
    
    # 2. Parallel Scanning Tasks
    parallel_tasks = [
        "skills_scan.py",
        "threat_intel.py",
        "sbom.py",
        "config_drift.py"
    ]
    
    logger.info(f"Running {len(parallel_tasks)} tasks in parallel...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(run_script, parallel_tasks))
    
    # 3. Post-processing (Sequential)
    # Run official OpenClaw audit
    logger.info("Running OpenClaw official security audit...")
    try:
        audit_res = subprocess.run(["openclaw", "security", "audit", "--deep", "--json"], 
                                 capture_output=True, text=True, timeout=180)
        if audit_res.returncode == 0:
            ts = time.strftime("%Y%m%d-%H%M%S")
            audit_file = REPORTS / f"openclaw-security-audit-{ts}.json"
            audit_file.write_text(audit_res.stdout)
            
            # Update meta.json
            meta = {}
            if (REPORTS / "meta.json").exists():
                meta = json.loads((REPORTS / "meta.json").read_text())
            meta["security_audit"] = {"latest": str(audit_file), "timestamp": ts, "status": "success"}
            (REPORTS / "meta.json").write_text(json.dumps(meta, indent=2))
    except Exception as e:
        logger.error(f"OpenClaw audit failed: {e}")

    # Final Score and Dashboard
    run_script("risk_score.py")
    run_script("auto_fix.py", ["--execute"]) # Execute fixes if configured
    run_script("html_dashboard.py")
    run_script("cleanup_reports.py")

    duration = time.time() - start_time
    logger.info(f"=== Daily Run Completed in {duration:.1f}s ===")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
