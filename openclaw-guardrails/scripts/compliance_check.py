#!/usr/bin/env python3
"""Compliance Check: Verify against security standards.

Checks:
- 等保 2.0 (MLPS 2.0) - Basic requirements for Level 2
- CIS Benchmarks - macOS/Ubuntu basic hardening
- OpenClaw Security Best Practices

Outputs:
- reports/compliance-<ts>.json
- reports/compliance-<ts>.md
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
OUT_JSON = REPORTS / f"compliance-{TS}.json"
OUT_MD = REPORTS / f"compliance-{TS}.md"


def check_file_permissions(path: Path, expected_mode: int) -> Tuple[bool, str]:
    """Check if file has expected permissions."""
    if not path.exists():
        return False, "File not found"
    
    try:
        actual_mode = path.stat().st_mode & 0o777
        if actual_mode == expected_mode:
            return True, f"Mode {oct(actual_mode)}"
        else:
            return False, f"Expected {oct(expected_mode)}, got {oct(actual_mode)}"
    except Exception as e:
        return False, str(e)


def check_openclaw_config() -> List[Dict[str, Any]]:
    """Check OpenClaw configuration against security best practices."""
    findings = []
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    
    if not config_path.exists():
        findings.append({
            "id": "OC-001",
            "standard": "OpenClaw Best Practices",
            "title": "Configuration file missing",
            "severity": "high",
            "status": "fail",
            "remediation": "Ensure ~/.openclaw/openclaw.json exists",
        })
        return findings
    
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        findings.append({
            "id": "OC-001",
            "standard": "OpenClaw Best Practices",
            "title": "Configuration file is invalid JSON",
            "severity": "high",
            "status": "fail",
            "remediation": "Fix JSON syntax in ~/.openclaw/openclaw.json",
        })
        return findings
    
    # Check gateway bind
    gateway = config.get("gateway", {})
    bind = gateway.get("bind", "unknown")
    if bind == "0.0.0.0":
        findings.append({
            "id": "OC-002",
            "standard": "OpenClaw Best Practices",
            "title": "Gateway bound to all interfaces",
            "severity": "high",
            "status": "fail",
            "detail": "gateway.bind = 0.0.0.0",
            "remediation": "Set gateway.bind to 'loopback' or specific IP",
        })
    elif bind == "loopback":
        findings.append({
            "id": "OC-002",
            "standard": "OpenClaw Best Practices",
            "title": "Gateway bound to loopback",
            "severity": "info",
            "status": "pass",
            "detail": "gateway.bind = loopback",
        })
    
    # Check groupPolicy
    channels = config.get("channels", {})
    for channel_type, channel_config in channels.items():
        if isinstance(channel_config, dict):
            group_policy = channel_config.get("groupPolicy", "")
            if group_policy == "open":
                findings.append({
                    "id": f"OC-003-{channel_type}",
                    "standard": "OpenClaw Best Practices",
                    "title": f"Channel {channel_type} has open group policy",
                    "severity": "high",
                    "status": "fail",
                    "remediation": f"Set channels.{channel_type}.groupPolicy to 'allowlist'",
                })
    
    # Check tools.elevated
    tools = config.get("tools", {})
    if tools.get("profile") == "full":
        findings.append({
            "id": "OC-004",
            "standard": "OpenClaw Best Practices",
            "title": "Full tool profile enabled",
            "severity": "medium",
            "status": "warning",
            "detail": "tools.profile = full",
            "remediation": "Consider using 'messaging' or 'coding' profile for untrusted inputs",
        })
    
    return findings


def check_mlps2_basic() -> List[Dict[str, Any]]:
    """Check basic 等保 2.0 Level 2 requirements."""
    findings = []
    
    # 1. Identity and Authentication
    # Check if OpenClaw has authentication enabled
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            gateway = config.get("gateway", {})
            auth = gateway.get("auth", {})
            if auth.get("mode") == "token":
                findings.append({
                    "id": "MLPS-AUTH-001",
                    "standard": "等保 2.0 Level 2 - Authentication",
                    "title": "Token-based authentication enabled",
                    "severity": "info",
                    "status": "pass",
                })
            else:
                findings.append({
                    "id": "MLPS-AUTH-001",
                    "standard": "等保 2.0 Level 2 - Authentication",
                    "title": "Authentication mode not configured",
                    "severity": "medium",
                    "status": "fail",
                    "remediation": "Set gateway.auth.mode to 'token'",
                })
        except Exception:
            pass
    
    # 2. Access Control
    # Check file permissions on config
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    passed, detail = check_file_permissions(config_path, 0o600)
    findings.append({
        "id": "MLPS-AC-001",
        "standard": "等保 2.0 Level 2 - Access Control",
        "title": "Configuration file permissions",
        "severity": "medium" if not passed else "info",
        "status": "pass" if passed else "fail",
        "detail": detail,
        "remediation": "Run: chmod 600 ~/.openclaw/openclaw.json",
    })
    
    # 3. Security Audit
    # Check if guardrails daily cron exists
    cron_check = subprocess.run(
        ["openclaw", "cron", "list"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if "guardrails:daily" in cron_check.stdout:
        findings.append({
            "id": "MLPS-AUDIT-001",
            "standard": "等保 2.0 Level 2 - Security Audit",
            "title": "Automated security monitoring enabled",
            "severity": "info",
            "status": "pass",
        })
    else:
        findings.append({
            "id": "MLPS-AUDIT-001",
            "standard": "等保 2.0 Level 2 - Security Audit",
            "title": "Automated security monitoring not configured",
            "severity": "medium",
            "status": "fail",
            "remediation": "Run: openclaw cron add --name guardrails:daily ...",
        })
    
    return findings


def check_cis_basic() -> List[Dict[str, Any]]:
    """Check basic CIS benchmark items (cross-platform)."""
    findings = []
    
    # 1. Check if firewall is enabled
    import platform
    system = platform.system()
    
    if system == "Darwin":  # macOS
        result = subprocess.run(
            ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "enabled" in result.stdout.lower():
            findings.append({
                "id": "CIS-FW-001",
                "standard": "CIS macOS Benchmark - Firewall",
                "title": "Application Firewall enabled",
                "severity": "info",
                "status": "pass",
            })
        else:
            findings.append({
                "id": "CIS-FW-001",
                "standard": "CIS macOS Benchmark - Firewall",
                "title": "Application Firewall disabled",
                "severity": "medium",
                "status": "fail",
                "remediation": "Enable in System Settings → Network → Firewall",
            })
    
    elif system == "Linux":
        result = subprocess.run(
            ["ufw", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "active" in result.stdout.lower():
            findings.append({
                "id": "CIS-FW-001",
                "standard": "CIS Ubuntu Benchmark - Firewall",
                "title": "UFW Firewall enabled",
                "severity": "info",
                "status": "pass",
            })
        else:
            findings.append({
                "id": "CIS-FW-001",
                "standard": "CIS Ubuntu Benchmark - Firewall",
                "title": "UFW Firewall disabled",
                "severity": "medium",
                "status": "fail",
                "remediation": "Run: sudo ufw enable",
            })
    
    # 2. Check automatic security updates
    # (Simplified check - just look for common update services)
    if system == "Darwin":
        findings.append({
            "id": "CIS-UPDATE-001",
            "standard": "CIS macOS Benchmark - Updates",
            "title": "Manual check required",
            "severity": "info",
            "status": "manual",
            "detail": "Verify in System Settings → General → Software Update",
            "remediation": "Enable automatic updates",
        })
    
    return findings


def gen_md_report(findings: List[Dict]) -> str:
    """Generate human-readable compliance report."""
    lines = []
    lines.append("# 📋 Compliance Check Report")
    lines.append(f"**Time**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Summary by standard
    by_standard = {}
    for f in findings:
        std = f.get("standard", "Unknown")
        if std not in by_standard:
            by_standard[std] = {"pass": 0, "fail": 0, "warning": 0, "manual": 0}
        status = f.get("status", "unknown")
        if status in by_standard[std]:
            by_standard[std][status] += 1
    
    lines.append("## Summary by Standard")
    for std, counts in sorted(by_standard.items()):
        total = sum(counts.values())
        lines.append(f"### {std}")
        lines.append(f"- ✅ Pass: {counts['pass']}")
        lines.append(f"- ❌ Fail: {counts['fail']}")
        lines.append(f"- ⚠️  Warning: {counts['warning']}")
        lines.append(f"- 📝 Manual: {counts['manual']}")
        lines.append(f"- **Total**: {total}")
        lines.append("")
    
    # Detailed findings
    lines.append("## Detailed Findings")
    
    # Group by status
    for status in ["fail", "warning", "manual", "pass"]:
        status_findings = [f for f in findings if f.get("status") == status]
        if not status_findings:
            continue
        
        emoji = {"fail": "❌", "warning": "⚠️", "manual": "📝", "pass": "✅"}[status]
        lines.append(f"### {emoji} {status.title()} ({len(status_findings)})")
        
        for f in status_findings:
            lines.append(f"#### {f.get('id', 'UNKNOWN')}: {f.get('title', 'Unknown')}")
            lines.append(f"- **Standard**: {f.get('standard', 'Unknown')}")
            lines.append(f"- **Severity**: {f.get('severity', 'unknown')}")
            if f.get("detail"):
                lines.append(f"- **Detail**: {f['detail']}")
            if f.get("remediation"):
                lines.append(f"- **Fix**: {f['remediation']}")
            lines.append("")
    
    lines.append("---")
    lines.append("*Generated by openclaw-guardrails compliance_check.py*")
    
    return "\n".join(lines)


def main() -> int:
    print("📋 Running compliance checks...")
    
    all_findings = []
    
    # OpenClaw Best Practices
    print("  - Checking OpenClaw configuration...")
    oc_findings = check_openclaw_config()
    all_findings.extend(oc_findings)
    print(f"    Found: {len(oc_findings)} checks")
    
    # 等保 2.0 Basic
    print("  - Checking 等保 2.0 Level 2 requirements...")
    mlps_findings = check_mlps2_basic()
    all_findings.extend(mlps_findings)
    print(f"    Found: {len(mlps_findings)} checks")
    
    # CIS Basic
    print("  - Checking CIS Benchmark basics...")
    cis_findings = check_cis_basic()
    all_findings.extend(cis_findings)
    print(f"    Found: {len(cis_findings)} checks")
    
    # Generate report
    md_report = gen_md_report(all_findings)
    OUT_MD.write_text(md_report, encoding="utf-8")
    
    OUT_JSON.write_text(json.dumps({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "findings": all_findings,
        "summary": {
            "total": len(all_findings),
            "pass": len([f for f in all_findings if f.get("status") == "pass"]),
            "fail": len([f for f in all_findings if f.get("status") == "fail"]),
            "warning": len([f for f in all_findings if f.get("status") == "warning"]),
            "manual": len([f for f in all_findings if f.get("status") == "manual"]),
        }
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"\n✅ Saved: {OUT_JSON}")
    print(f"✅ Saved: {OUT_MD}")
    
    print(f"\n📊 Summary:")
    print(f"  Total: {len(all_findings)}")
    print(f"  Pass: {len([f for f in all_findings if f.get('status') == 'pass'])}")
    print(f"  Fail: {len([f for f in all_findings if f.get('status') == 'fail'])}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
