#!/usr/bin/env python3
"""Auto-Remediation: Automatically fix low-risk security issues.

Auto-fix categories (no confirmation required):
- Dependency upgrades (npm update, pip install --upgrade)
- Config restoration to secure baseline (groupPolicy, etc.)

Requires confirmation:
- Uninstall skills
- Major config changes

Never auto-fix:
- Download/execute external scripts
- Firewall/network changes
- System-level changes

Outputs:
- reports/auto-fix-<ts>.json
- reports/auto-fix-<ts>.md
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
OUT_JSON = REPORTS / f"auto-fix-{TS}.json"
OUT_MD = REPORTS / f"auto-fix-{TS}.md"

# Config paths that can be auto-fixed
AUTO_FIX_CONFIG = {
    "groupPolicy": {
        "unsafe_value": "open",
        "safe_value": "allowlist",
        "cli_template": "openclaw config set {path}=allowlist",
    },
    "tools.fs.workspaceOnly": {
        "unsafe_value": False,
        "safe_value": True,
        "cli_template": "openclaw config set {path}=true",
    },
}

# Dependency upgrade commands
DEP_UPGRADE_COMMANDS = {
    "npm": "npm update --prefix {path}",
    "pip": "pip install --upgrade -r {path}/requirements.txt",
}


def load_drift_report() -> List[Dict]:
    """Load latest config drift report."""
    drift_files = sorted(REPORTS.glob("config-drift-*.json"))
    if not drift_files:
        return []
    try:
        data = json.loads(drift_files[-1].read_text(encoding="utf-8"))
        return data.get("drifts", [])
    except Exception:
        return []


def load_threat_intel() -> List[Dict]:
    """Load latest threat intelligence report."""
    intel_files = sorted(REPORTS.glob("threat-intel-*.json"))
    if not intel_files:
        return []
    try:
        data = json.loads(intel_files[-1].read_text(encoding="utf-8"))
        return data.get("vulnerabilities", [])
    except Exception:
        return []


def auto_fix_config(drifts: List[Dict], execute: bool = False) -> Tuple[List[Dict], List[Dict]]:
    """Auto-fix configuration drifts.
    
    Args:
        drifts: List of configuration drifts
        execute: If True, actually execute fixes. If False, simulate only.
    
    Returns:
        (fixed, failed) lists
    """
    fixed = []
    failed = []

    for drift in drifts:
        path = drift.get("path", "")
        current = drift.get("current")
        expected = drift.get("expected")

        # Check if this config can be auto-fixed
        can_auto_fix = False
        for config_path, rules in AUTO_FIX_CONFIG.items():
            if path.endswith(config_path):
                if current == rules["unsafe_value"] and expected == rules["safe_value"]:
                    can_auto_fix = True
                    break

        if not can_auto_fix:
            continue

        # Execute fix command
        cli_cmd = f"openclaw config set {path}={json.dumps(expected)}"
        print(f"  - Auto-fixing: {path} ({current} → {expected})")

        if not execute:
            # Simulate only
            fixed.append({
                "path": path,
                "from": current,
                "to": expected,
                "command": cli_cmd,
                "status": "simulated",
            })
            continue

        try:
            # Actually execute
            result = subprocess.run(
                cli_cmd.split(),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                fixed.append({
                    "path": path,
                    "from": current,
                    "to": expected,
                    "command": cli_cmd,
                    "status": "executed",
                    "output": result.stdout.strip(),
                })
            else:
                failed.append({
                    "path": path,
                    "command": cli_cmd,
                    "error": result.stderr.strip(),
                    "status": "failed",
                })
        except Exception as e:
            failed.append({
                "path": path,
                "error": str(e),
                "status": "exception",
            })

    return fixed, failed


def auto_upgrade_deps(vulns: List[Dict], execute: bool = False) -> Tuple[List[Dict], List[Dict]]:
    """Auto-upgrade vulnerable dependencies.
    
    Args:
        vulns: List of vulnerabilities
        execute: If True, actually execute upgrades. If False, simulate only.
    
    Returns:
        (upgraded, failed) lists
    """
    upgraded = []
    failed = []

    # Group vulns by ecosystem and source
    by_ecosystem = {}
    for v in vulns:
        eco = v.get("ecosystem", "unknown")
        src = v.get("source", "unknown")
        pkg = v.get("package", v.get("queried_package", "unknown"))

        if eco not in by_ecosystem:
            by_ecosystem[eco] = {}
        if src not in by_ecosystem[eco]:
            by_ecosystem[eco][src] = []
        by_ecosystem[eco][src].append(pkg)

    # Execute upgrades
    for eco, sources in by_ecosystem.items():
        if eco not in DEP_UPGRADE_COMMANDS:
            continue

        cmd_template = DEP_UPGRADE_COMMANDS[eco]
        for src, packages in sources.items():
            print(f"  - Upgrading {eco} deps in {src}: {', '.join(packages[:5])}")

            if not execute:
                # Simulate only
                cmd = cmd_template.format(path=src)
                upgraded.append({
                    "ecosystem": eco,
                    "source": src,
                    "packages": packages[:10],
                    "command": cmd,
                    "status": "simulated",
                })
                continue

            try:
                cmd = cmd_template.format(path=src)
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=src,
                )
                if result.returncode == 0:
                    upgraded.append({
                        "ecosystem": eco,
                        "source": src,
                        "packages": packages[:10],
                        "command": cmd,
                        "status": "executed",
                        "output": result.stdout.strip(),
                    })
                else:
                    failed.append({
                        "ecosystem": eco,
                        "source": src,
                        "command": cmd,
                        "error": result.stderr.strip(),
                        "status": "failed",
                    })
            except Exception as e:
                failed.append({
                    "ecosystem": eco,
                    "source": src,
                    "error": str(e),
                    "status": "exception",
                })

    return upgraded, failed


def gen_md_report(fixed: List, failed: List, upgraded: List, upgrade_failed: List) -> str:
    """Generate human-readable markdown report."""
    lines = []
    lines.append("# 🔧 Auto-Fix Report")
    lines.append(f"**Time**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## Summary")
    lines.append(f"- ✅ Config Fixed: {len(fixed)}")
    lines.append(f"- ❌ Config Fix Failed: {len(failed)}")
    lines.append(f"- 📦 Dependencies Upgraded: {len(upgraded)}")
    lines.append(f"- 📦 Upgrade Failed: {len(upgrade_failed)}")
    lines.append("")

    if fixed:
        lines.append("## ✅ Configuration Fixes")
        for f in fixed:
            lines.append(f"- `{f['path']}`: `{f['from']}` → `{f['to']}`")
            lines.append(f"  - Command: `{f['command']}`")
            if f.get("status") == "simulated":
                lines.append(f"  - ⚠️  Status: Simulated (not executed)")
        lines.append("")

    if upgraded:
        lines.append("## 📦 Dependency Upgrades")
        for u in upgraded:
            lines.append(f"- **{u['ecosystem']}** in `{u['source']}`")
            lines.append(f"  - Packages: {', '.join(u['packages'][:5])}")
            lines.append(f"  - Command: `{u['command']}`")
            if u.get("status") == "simulated":
                lines.append(f"  - ⚠️  Status: Simulated (not executed)")
        lines.append("")

    if failed or upgrade_failed:
        lines.append("## ❌ Failures")
        for f in failed + upgrade_failed:
            lines.append(f"- {f.get('path', f.get('source', 'unknown'))}: {f.get('error', 'unknown error')}")
        lines.append("")

    if not fixed and not upgraded:
        lines.append("ℹ️  No auto-fixes were needed or applicable.")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by openclaw-guardrails auto_fix.py*")

    return "\n".join(lines)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Auto-remediation for OpenClaw security issues")
    ap.add_argument("--execute", action="store_true", help="Actually execute fixes (default: simulate only)")
    ap.add_argument("--dry-run", action="store_true", help="Simulate only (same as default)")
    args = ap.parse_args()

    execute = args.execute and not args.dry_run

    print("🔧 Running auto-remediation...")
    if not execute:
        print("⚠️  DRY RUN MODE - No changes will be made")
        print("   Use --execute to actually apply fixes\n")

    all_fixed = []
    all_failed = []
    all_upgraded = []
    all_upgrade_failed = []

    # Load reports
    print("  - Loading config drift report...")
    drifts = load_drift_report()
    print(f"    Found: {len(drifts)} drifts")

    print("  - Loading threat intel report...")
    vulns = load_threat_intel()
    print(f"    Found: {len(vulns)} vulnerabilities")

    # Auto-fix config
    print("\n  - Auto-fixing configuration...")
    fixed, failed = auto_fix_config(drifts, execute=execute)
    all_fixed.extend(fixed)
    all_failed.extend(failed)
    print(f"    Fixed: {len(fixed)}, Failed: {len(failed)}")

    # Auto-upgrade deps
    print("\n  - Auto-upgrading dependencies...")
    upgraded, upgrade_failed = auto_upgrade_deps(vulns, execute=execute)
    all_upgraded.extend(upgraded)
    all_upgrade_failed.extend(upgrade_failed)
    print(f"    Upgraded: {len(upgraded)}, Failed: {len(upgrade_failed)}")

    # Generate report
    md_report = gen_md_report(all_fixed, all_failed, all_upgraded, all_upgrade_failed)
    OUT_MD.write_text(md_report, encoding="utf-8")

    OUT_JSON.write_text(json.dumps({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "execute_mode": execute,
        "config_fixes": {
            "fixed": all_fixed,
            "failed": all_failed,
        },
        "dependency_upgrades": {
            "upgraded": all_upgraded,
            "failed": all_upgrade_failed,
        },
        "summary": {
            "config_fixed": len(all_fixed),
            "config_failed": len(all_failed),
            "deps_upgraded": len(all_upgraded),
            "deps_failed": len(all_upgrade_failed),
        }
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ Saved: {OUT_JSON}")
    print(f"✅ Saved: {OUT_MD}")

    if execute and (all_fixed or all_upgraded):
        print("\n🎉 Auto-remediation completed successfully!")
    elif not execute:
        print("\n💡 Run with --execute to actually apply these fixes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
