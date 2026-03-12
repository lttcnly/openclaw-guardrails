#!/usr/bin/env python3
"""Configuration Drift Detection.

Compares current OpenClaw configuration against a secure baseline.
Detects if unsafe settings were reverted after being fixed.

Outputs:
- reports/config-drift-<ts>.json
- reports/config-drift-<ts>.md
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
OUT_JSON = REPORTS / f"config-drift-{TS}.json"
OUT_MD = REPORTS / f"config-drift-{TS}.md"

# Secure baseline values
SECURE_BASELINE = {
    "groupPolicy": "allowlist",  # Should NOT be "open"
    "sandbox.mode": "all",  # Should be "all" for exposed agents
    "tools.fs.workspaceOnly": True,  # Should be True
    "gateway.bind": "loopback",  # Should NOT be "0.0.0.0"
}

# Paths to check
CONFIG_PATHS = [
    Path.home() / ".openclaw" / "openclaw.json",
]


def deep_get(d: Dict, path: str) -> Any:
    """Get nested dict value using dot notation."""
    keys = path.split(".")
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return None
    return cur


def find_all_paths(d: Dict, prefix: str = "") -> List[Tuple[str, Any]]:
    """Recursively find all config paths and values."""
    results = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                results.extend(find_all_paths(v, new_prefix))
            else:
                results.append((new_prefix, v))
    return results


def check_drift(config: Dict, baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for configuration drift from secure baseline."""
    drifts = []

    # Check explicit baseline paths
    for path, secure_value in baseline.items():
        current_value = deep_get(config, path)
        if current_value is None:
            continue
        if current_value != secure_value:
            drifts.append({
                "path": path,
                "current": current_value,
                "expected": secure_value,
                "severity": "critical" if path == "groupPolicy" else "warn",
                "fix": f"Set {path} to {json.dumps(secure_value)}",
            })

    # Check for "open" groupPolicy anywhere in config
    all_paths = find_all_paths(config)
    for path, value in all_paths:
        if path.endswith("groupPolicy") and value == "open":
            # Already captured above if in baseline
            if not any(d["path"] == path for d in drifts):
                drifts.append({
                    "path": path,
                    "current": value,
                    "expected": "allowlist",
                    "severity": "critical",
                    "fix": f"Set {path} to 'allowlist'",
                })

    return drifts


def gen_fix_commands(drifts: List[Dict]) -> List[str]:
    """Generate openclaw CLI commands to fix drifts."""
    fixes = []
    for d in drifts:
        path = d["path"]
        expected = d["expected"]

        # Convert dot notation to CLI command
        if path.startswith("channels."):
            # e.g., channels.discord.accounts.default.groupPolicy
            fixes.append(f"`openclaw config set {path}={json.dumps(expected)}`")
        elif path.startswith("gateway."):
            fixes.append(f"`openclaw gateway config set {path}={json.dumps(expected)}`")
        elif path.startswith("tools."):
            fixes.append(f"`openclaw tools config set {path}={json.dumps(expected)}`")
        elif path.startswith("sandbox."):
            fixes.append(f"`openclaw agents config set {path}={json.dumps(expected)}`")

    return fixes[:10]  # Limit to top 10


def gen_md_report(drifts: List[Dict], fixes: List[str]) -> str:
    """Generate human-readable markdown report."""
    lines = []
    lines.append("# 📊 Configuration Drift Report")
    lines.append(f"**Time**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    critical = [d for d in drifts if d.get("severity") == "critical"]
    warns = [d for d in drifts if d.get("severity") == "warn"]

    lines.append("## Summary")
    lines.append(f"- 🔴 Critical Drifts: {len(critical)}")
    lines.append(f"- 🟡 Warnings: {len(warns)}")
    lines.append("")

    if critical:
        lines.append("## 🔴 Critical Drifts")
        for d in critical:
            lines.append(f"- **{d['path']}**")
            lines.append(f"  - Current: `{d['current']}`")
            lines.append(f"  - Expected: `{d['expected']}`")
            lines.append(f"  - Fix: {d['fix']}")
        lines.append("")

    if warns:
        lines.append("## 🟡 Warnings")
        for d in warns:
            lines.append(f"- **{d['path']}**: `{d['current']}` → should be `{d['expected']}`")
        lines.append("")

    if fixes:
        lines.append("## 🔧 Quick Fixes")
        for fix in fixes:
            lines.append(fix)
        lines.append("")

    if not drifts:
        lines.append("✅ No configuration drift detected. Your config matches the secure baseline.")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by openclaw-guardrails config_drift.py*")

    return "\n".join(lines)


def main() -> int:
    print("📊 Checking for configuration drift...")

    all_drifts = []

    for config_path in CONFIG_PATHS:
        if not config_path.exists():
            print(f"  - Config not found: {config_path}")
            continue

        print(f"  - Checking: {config_path}")
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            drifts = check_drift(config, SECURE_BASELINE)
            for d in drifts:
                d["config_file"] = str(config_path)
            all_drifts.extend(drifts)
            print(f"    Found: {len(drifts)} drifts")
        except Exception as e:
            print(f"    Error: {e}")

    fixes = gen_fix_commands(all_drifts)

    # Save JSON
    OUT_JSON.write_text(json.dumps({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config_files": [str(p) for p in CONFIG_PATHS],
        "drifts": all_drifts,
        "fixes": fixes,
        "summary": {
            "total": len(all_drifts),
            "critical": len([d for d in all_drifts if d.get("severity") == "critical"]),
            "warn": len([d for d in all_drifts if d.get("severity") == "warn"]),
        }
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # Save MD
    md_report = gen_md_report(all_drifts, fixes)
    OUT_MD.write_text(md_report, encoding="utf-8")

    print(f"\n✅ Saved: {OUT_JSON}")
    print(f"✅ Saved: {OUT_MD}")
    print(f"\n📊 Summary: {len(all_drifts)} drifts ({len([d for d in all_drifts if d.get('severity') == 'critical'])} critical)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
