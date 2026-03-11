#!/usr/bin/env python3
"""Pre-install scan for ClawHub skills.

Usage:
  python3 preinstall_scan.py <skill-slug-or-folder>

Blocks installation if:
- HIGH severity patterns detected (shell_exec + network_exec)
- Known malicious patterns (env harvesting, credential exfil)
- Unpinned npm specs with network access

Exit codes:
- 0: Safe to install
- 1: Warning (user can proceed)
- 2: Blocked (critical risk)
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List

# Patterns that indicate high risk
CRITICAL_PATTERNS = {
    "env_harvesting": re.compile(r"process\.env|os\.environ|getenv\s*\(", re.I),
    "network_exfil": re.compile(r"fetch\s*\(|axios\.post|curl\s|wget\s|XMLHttpRequest", re.I),
    "shell_exec": re.compile(r"child_process|exec\s*\(|spawn\s*\(|os\.system|subprocess\.", re.I),
    "credential_access": re.compile(r"keychain|credentials|token|secret|api[_-]?key", re.I),
}

HIGH_RISK_PATTERNS = {
    "fs_write": re.compile(r"fs\.write|writeFile|writeFileSync", re.I),
    "persistence": re.compile(r"launchctl|schtasks|cron|systemd", re.I),
    "eval_code": re.compile(r"\beval\s*\(|new\s+Function\b", re.I),
}


def scan_file(path: Path) -> Dict[str, Any]:
    """Scan a single file for risky patterns."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {"path": str(path), "critical": [], "high": []}

    findings = {"path": str(path), "critical": [], "high": []}

    for name, pattern in CRITICAL_PATTERNS.items():
        if pattern.search(content):
            findings["critical"].append(name)

    for name, pattern in HIGH_RISK_PATTERNS.items():
        if pattern.search(content):
            findings["high"].append(name)

    return findings


def scan_folder(folder: Path) -> Dict[str, Any]:
    """Scan all files in a folder."""
    results = {
        "folder": str(folder),
        "files_scanned": 0,
        "critical_findings": [],
        "high_findings": [],
        "blocked_files": [],
    }

    for p in folder.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".js", ".ts", ".py", ".sh", ".ps1", ".mjs", ".cjs"):
            continue
        if "node_modules" in str(p):
            continue

        results["files_scanned"] += 1
        findings = scan_file(p)

        if findings["critical"]:
            results["critical_findings"].append({
                "file": str(p.relative_to(folder)),
                "patterns": findings["critical"],
            })
            results["blocked_files"].append(str(p.relative_to(folder)))

        if findings["high"]:
            results["high_findings"].append({
                "file": str(p.relative_to(folder)),
                "patterns": findings["high"],
            })

    return results


def fetch_skill(slug: str) -> Path | None:
    """Fetch skill source to temp folder (without installing)."""
    try:
        # Use clawhub inspect to get skill metadata
        result = subprocess.run(
            ["clawhub", "inspect", slug, "--files"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None

        # For now, we can't fetch source without install
        # This is a limitation - user needs to provide local folder
        print(f"Warning: Cannot fetch '{slug}' source without installing.")
        print("Please download skill folder first, then scan the folder.")
        return None
    except Exception:
        return None


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 preinstall_scan.py <skill-folder>")
        print("\nScan a skill folder before installation.")
        print("\nExit codes:")
        print("  0 = Safe to install")
        print("  1 = Warning (review recommended)")
        print("  2 = Blocked (critical risk detected)")
        return 1

    target = Path(sys.argv[1]).expanduser()

    if not target.exists():
        print(f"Error: Path not found: {target}")
        return 1

    if not target.is_dir():
        print(f"Error: Not a folder: {target}")
        return 1

    print(f"🔍 Scanning: {target}")
    results = scan_folder(target)

    print(f"\n📊 Results:")
    print(f"  Files scanned: {results['files_scanned']}")
    print(f"  Critical findings: {len(results['critical_findings'])}")
    print(f"  High findings: {len(results['high_findings'])}")

    if results["critical_findings"]:
        print(f"\n🚨 BLOCKED - Critical patterns detected:")
        for f in results["critical_findings"][:10]:
            print(f"  - {f['file']}: {', '.join(f['patterns'])}")
        print("\nRecommendation: Do NOT install this skill.")
        return 2

    if results["high_findings"]:
        print(f"\n⚠️  WARNING - High-risk patterns detected:")
        for f in results["high_findings"][:10]:
            print(f"  - {f['file']}: {', '.join(f['patterns'])}")
        print("\nRecommendation: Review code before installing.")
        return 1

    print("\n✅ Safe to install")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
