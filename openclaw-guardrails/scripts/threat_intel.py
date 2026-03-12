#!/usr/bin/env python3
"""Threat Intelligence: Scan dependencies for known vulnerabilities.

Data sources:
- OSV.dev API (free, Google-maintained)
- npm audit (local)
- pip-audit (if available)
- GitHub Security Advisories (via API)

Outputs:
- reports/threat-intel-<ts>.json
- reports/threat-intel-<ts>.md (human readable)
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
OUT_JSON = REPORTS / f"threat-intel-{TS}.json"
OUT_MD = REPORTS / f"threat-intel-{TS}.md"

# Paths to scan
SCAN_PATHS = [
    Path.home() / ".openclaw",
    Path.home() / ".openclaw" / "skills",
    Path.home() / ".openclaw" / "extensions",
]


def scan_npm_vulns() -> List[Dict[str, Any]]:
    """Scan Node.js dependencies using npm audit."""
    vulns = []
    for path in SCAN_PATHS:
        if not path.exists():
            continue
        pkg_lock = path / "package-lock.json"
        if pkg_lock.exists():
            try:
                result = subprocess.run(
                    ["npm", "audit", "--json"],
                    cwd=str(path),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for vuln in data.get("vulnerabilities", {}).values():
                        vuln["source"] = str(path)
                        vuln["type"] = "npm"
                        vulns.append(vuln)
            except Exception as e:
                pass  # Skip if npm not available or audit fails
    return vulns


def scan_pip_vulns() -> List[Dict[str, Any]]:
    """Scan Python dependencies using pip-audit (if available)."""
    vulns = []
    # Check if pip-audit is available
    try:
        result = subprocess.run(
            ["pip-audit", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return vulns  # pip-audit not installed
    except Exception:
        return vulns

    for path in SCAN_PATHS:
        if not path.exists():
            continue
        req_txt = path / "requirements.txt"
        if req_txt.exists():
            try:
                result = subprocess.run(
                    ["pip-audit", "-r", str(req_txt), "-f", "json"],
                    cwd=str(path),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for dep, versions in data.items():
                        for vuln in versions:
                            vuln["package"] = dep
                            vuln["source"] = str(path)
                            vuln["type"] = "pip"
                            vulns.append(vuln)
            except Exception as e:
                pass
    return vulns


def scan_osv_vulns() -> List[Dict[str, Any]]:
    """Query OSV.dev API for known vulnerabilities in common packages."""
    vulns = []
    # Common packages used by OpenClaw
    packages = [
        {"name": "openclaw", "ecosystem": "npm"},
        {"name": "express", "ecosystem": "npm"},
        {"name": "axios", "ecosystem": "npm"},
        {"name": "requests", "ecosystem": "PyPI"},
        {"name": "flask", "ecosystem": "PyPI"},
    ]

    for pkg in packages:
        try:
            url = f"https://api.osv.dev/v1/query"
            data = json.dumps({"package": {"name": pkg["name"], "ecosystem": pkg["ecosystem"]}}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                for vuln in result.get("vulns", []):
                    vuln["queried_package"] = pkg["name"]
                    vuln["ecosystem"] = pkg["ecosystem"]
                    vulns.append(vuln)
        except Exception:
            pass  # Skip on network errors

    return vulns[:50]  # Limit to top 50


def scan_nvd_cve() -> List[Dict[str, Any]]:
    """Query NVD CVE API for recent critical vulnerabilities."""
    vulns = []
    try:
        # NVD API for CVEs from last 7 days with high severity
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        params = {
            "lastModStartDate": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "lastModEndDate": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "cvssV3Severity": "CRITICAL,HIGH",
        }
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        full_url = f"{url}?{query}"
        
        req = urllib.request.Request(full_url, headers={"User-Agent": "OpenClaw-Guardrails"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            for cve in result.get("vulnerabilities", [])[:20]:  # Limit to 20
                cve_data = cve.get("cve", {})
                vulns.append({
                    "id": cve_data.get("id", "UNKNOWN"),
                    "summary": cve_data.get("descriptions", [{}])[0].get("value", ""),
                    "severity": "critical",
                    "source": "NVD",
                    "type": "nvd_cve",
                })
    except Exception:
        pass  # Skip on errors

    return vulns


def scan_github_advisories() -> List[Dict[str, Any]]:
    """Query GitHub Security Advisories for npm/PyPI vulnerabilities."""
    vulns = []
    try:
        url = "https://api.github.com/advisories"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "OpenClaw-Guardrails",
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            for advisory in result[:20]:  # Limit to 20
                vulns.append({
                    "id": advisory.get("ghsa_id", "UNKNOWN"),
                    "summary": advisory.get("summary", ""),
                    "severity": advisory.get("severity", "unknown"),
                    "source": "GitHub Advisories",
                    "type": "github_advisory",
                    "ecosystem": advisory.get("ecosystem", "unknown"),
                })
    except Exception:
        pass  # Skip on errors

    return vulns


def summarize_vulns(vulns: List[Dict]) -> Dict[str, Any]:
    """Summarize vulnerabilities by severity."""
    summary = {
        "total": len(vulns),
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "by_ecosystem": {},
        "by_source": {},
    }

    for v in vulns:
        severity = v.get("severity", [{}])[0].get("severity", "UNKNOWN").lower()
        if severity in ("critical", "high", "medium", "low"):
            summary[severity] = summary.get(severity, 0) + 1

        eco = v.get("ecosystem", "unknown")
        summary["by_ecosystem"][eco] = summary["by_ecosystem"].get(eco, 0) + 1

        src = v.get("source", "unknown")
        summary["by_source"][src] = summary["by_source"].get(src, 0) + 1

    return summary


def gen_fixes(vulns: List[Dict]) -> List[str]:
    """Generate fix commands for vulnerabilities."""
    fixes = []
    seen = set()

    for v in vulns:
        if v.get("severity", [{}])[0].get("severity", "").lower() not in ("critical", "high"):
            continue

        pkg = v.get("package", v.get("queried_package", "unknown"))
        ecosystem = v.get("ecosystem", "unknown")
        fixed_version = v.get("database_specific", {}).get("fixed_version")

        key = f"{ecosystem}:{pkg}"
        if key in seen:
            continue
        seen.add(key)

        if ecosystem == "npm" and fixed_version:
            fixes.append(f"`npm update {pkg}@{fixed_version}`")
        elif ecosystem == "PyPI" and fixed_version:
            fixes.append(f"`pip install {pkg}=={fixed_version}`")
        elif ecosystem == "npm":
            fixes.append(f"`npm audit fix` (for {pkg})")

    return fixes[:10]  # Limit to top 10 fixes


def gen_md_report(summary: Dict, vulns: List[Dict], fixes: List[str]) -> str:
    """Generate human-readable markdown report."""
    lines = []
    lines.append("# 🔍 Threat Intelligence Report")
    lines.append(f"**Time**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## Summary")
    lines.append(f"- **Total Vulnerabilities**: {summary['total']}")
    lines.append(f"- 🔴 Critical: {summary.get('critical', 0)}")
    lines.append(f"- 🟠 High: {summary.get('high', 0)}")
    lines.append(f"- 🟡 Medium: {summary.get('medium', 0)}")
    lines.append(f"- 🟢 Low: {summary.get('low', 0)}")
    lines.append("")

    if summary["by_ecosystem"]:
        lines.append("## By Ecosystem")
        for eco, count in sorted(summary["by_ecosystem"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {eco}: {count}")
        lines.append("")

    if fixes:
        lines.append("## 🔧 Quick Fixes")
        for fix in fixes:
            lines.append(fix)
        lines.append("")

    # Top 10 critical vulns
    critical_vulns = [v for v in vulns if v.get("severity", [{}])[0].get("severity", "").lower() == "critical"][:10]
    if critical_vulns:
        lines.append("## Critical Vulnerabilities")
        for v in critical_vulns:
            pkg = v.get("package", v.get("queried_package", "unknown"))
            vuln_id = v.get("id", "UNKNOWN")
            summary_text = v.get("summary", "No summary")
            lines.append(f"- **{vuln_id}** ({pkg}): {summary_text[:100]}")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by openclaw-guardrails threat_intel.py*")

    return "\n".join(lines)


def main() -> int:
    print("🔍 Scanning for dependency vulnerabilities...")

    all_vulns = []

    # Scan npm
    print("  - Scanning npm dependencies...")
    npm_vulns = scan_npm_vulns()
    all_vulns.extend(npm_vulns)
    print(f"    Found: {len(npm_vulns)}")

    # Scan pip
    print("  - Scanning Python dependencies...")
    pip_vulns = scan_pip_vulns()
    all_vulns.extend(pip_vulns)
    print(f"    Found: {len(pip_vulns)}")

    # Query OSV
    print("  - Querying OSV.dev API...")
    osv_vulns = scan_osv_vulns()
    all_vulns.extend(osv_vulns)
    print(f"    Found: {len(osv_vulns)}")

    # Query NVD CVE (NEW)
    print("  - Querying NVD CVE API...")
    nvd_vulns = scan_nvd_cve()
    all_vulns.extend(nvd_vulns)
    print(f"    Found: {len(nvd_vulns)}")

    # Query GitHub Advisories (NEW)
    print("  - Querying GitHub Security Advisories...")
    gha_vulns = scan_github_advisories()
    all_vulns.extend(gha_vulns)
    print(f"    Found: {len(gha_vulns)}")

    # Summarize
    summary = summarize_vulns(all_vulns)
    fixes = gen_fixes(all_vulns)

    # Save JSON
    OUT_JSON.write_text(json.dumps({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary,
        "vulnerabilities": all_vulns[:100],  # Limit JSON size
        "fixes": fixes,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # Save MD
    md_report = gen_md_report(summary, all_vulns, fixes)
    OUT_MD.write_text(md_report, encoding="utf-8")

    print(f"\n✅ Saved: {OUT_JSON}")
    print(f"✅ Saved: {OUT_MD}")
    print(f"\n📊 Summary: {summary['total']} vulns ({summary.get('critical', 0)} critical, {summary.get('high', 0)} high)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
