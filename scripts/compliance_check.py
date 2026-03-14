#!/usr/bin/env python3
"""Compliance Check: Verify against security standards.

Checks:
- 等保 2.0 (MLPS 2.0) - Level 2 / Level 3 key requirements
- CIS Benchmarks - macOS/Linux hardening
- OpenClaw Security Best Practices

Outputs:
- reports/compliance-<ts>.json
- reports/compliance-<ts>.md
- updates reports/meta.json
"""

from __future__ import annotations

import json
import subprocess
import time
import logging
import platform
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
LOGS = ROOT / "logs"
REPORTS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOGS / "guardrails.log"), logging.StreamHandler()]
)
logger = logging.getLogger("compliance_check")

TS = time.strftime("%Y%m%d-%H%M%S")
OUT_JSON = REPORTS / f"compliance-{TS}.json"
OUT_MD = REPORTS / f"compliance-{TS}.md"
META_FILE = REPORTS / "meta.json"

def update_meta(report_type: str, file_path: Path):
    meta = {}
    if META_FILE.exists():
        try:
            meta = json.loads(META_FILE.read_text(encoding="utf-8"))
        except: pass
    meta[report_type] = {"latest": str(file_path), "timestamp": time.time(), "status": "success"}
    META_FILE.write_text(json.dumps(meta, indent=2), encoding="utf-8")

def check_file_permissions(path: Path, expected_mode: int) -> Tuple[bool, str]:
    if not path.exists(): return False, "File not found"
    try:
        actual_mode = path.stat().st_mode & 0o777
        return (actual_mode == expected_mode), f"Mode {oct(actual_mode)}"
    except Exception as e:
        return False, str(e)

def check_openclaw_hardening() -> List[Dict]:
    """Deep check of OpenClaw hardening (MLPS 2.0 Identity & Control)."""
    findings = []
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if not config_path.exists(): return findings

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        
        # 1. Identity & Auth (身份鉴别)
        auth = config.get("gateway", {}).get("auth", {})
        if auth.get("mode") != "token":
            findings.append({
                "id": "MLPS-ID-01", "standard": "MLPS 2.0", "severity": "high", "status": "fail",
                "title": "缺乏有效的身份鉴别机制", "remediation": "设置 gateway.auth.mode = 'token'"
            })
        
        # 2. Access Control (访问控制)
        # Check if discord groupPolicy is 'allowlist'
        discord_policy = config.get("channels", {}).get("discord", {}).get("groupPolicy")
        if discord_policy == "open":
            findings.append({
                "id": "MLPS-AC-01", "standard": "MLPS 2.0", "severity": "high", "status": "fail",
                "title": "敏感通道访问控制过松 (groupPolicy=open)", "remediation": "将 discord groupPolicy 设为 allowlist"
            })
            
        # 3. Security Audit (安全审计)
        hooks = config.get("hooks", {}).get("internal", {}).get("entries", {})
        if not hooks.get("command-logger", {}).get("enabled"):
            findings.append({
                "id": "MLPS-AU-01", "standard": "MLPS 2.0", "severity": "medium", "status": "fail",
                "title": "未开启指令审计日志", "remediation": "在 hooks.internal.entries 中开启 command-logger"
            })

        # 4. Intrusion Prevention (入侵防范)
        deny_cmds = config.get("gateway", {}).get("nodes", {}).get("denyCommands", [])
        if not deny_cmds:
             findings.append({
                "id": "MLPS-IP-01", "standard": "MLPS 2.0", "severity": "medium", "status": "fail",
                "title": "未配置敏感指令黑名单", "remediation": "在 gateway.nodes.denyCommands 中添加敏感指令"
            })

    except Exception as e:
        logger.error(f"Config hardening check failed: {e}")
    return findings

def check_system_hardening() -> List[Dict]:
    """Check System-level Hardening (CIS)."""
    findings = []
    sys_type = platform.system()
    
    # 1. Firewall Check
    if sys_type == "Darwin":
        res = subprocess.run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"], capture_output=True, text=True)
        active = "enabled" in res.stdout.lower()
    else:
        res = subprocess.run(["ufw", "status"], capture_output=True, text=True)
        active = "active" in res.stdout.lower()
    
    findings.append({
        "id": "CIS-NET-01", "standard": "CIS Benchmark", "severity": "medium", "status": "pass" if active else "fail",
        "title": "系统防火墙状态", "remediation": "开启系统级防火墙 (macOS SocketFilter / Linux UFW)"
    })

    # 2. Config File Permissions
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    passed, detail = check_file_permissions(config_path, 0o600)
    findings.append({
        "id": "CIS-FS-01", "standard": "CIS Benchmark", "severity": "medium", "status": "pass" if passed else "fail",
        "title": "配置文件权限审计", "detail": detail, "remediation": "chmod 600 ~/.openclaw/openclaw.json"
    })

    return findings

def main() -> int:
    logger.info("Starting Deep Compliance Check...")
    
    all_findings = []
    all_findings.extend(check_openclaw_hardening())
    all_findings.extend(check_system_hardening())
    
    summary = {
        "total": len(all_findings),
        "pass": len([f for f in all_findings if f["status"] == "pass"]),
        "fail": len([f for f in all_findings if f["status"] == "fail"]),
    }
    
    report = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary,
        "findings": all_findings
    }
    
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    update_meta("compliance_check", OUT_JSON)
    
    logger.info(f"Compliance check complete. Pass: {summary['pass']}, Fail: {summary['fail']}. Report: {OUT_JSON}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
