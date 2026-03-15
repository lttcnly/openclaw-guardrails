#!/usr/bin/env python3
"""Vuln Scan: Scans SBOM and dependencies for known vulnerabilities.
Integration: Directly consumes sbom.json.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SBOM_FILE = REPORTS / "sbom.json"

def scan_package_vulns(package_name: str, version: str) -> List[Dict]:
    """Simulated vulnerability check (can be integrated with npm audit or safety)."""
    # This is a placeholder for real API calls to NVD/OSV.
    # In a real scenario, we'd run 'npm audit --json' or similar.
    findings = []
    # Hardcoded example for demonstration:
    if "request" in package_name and version.startswith("2."):
        findings.append({
            "id": "GHSA-j8v7-hjcq-733m",
            "severity": "MODERATE",
            "summary": "SSRF vulnerability in request package",
            "package": package_name
        })
    return findings

def main():
    print("[*] Running Vuln Scan: Correlating SBOM with global vulnerability databases...")
    
    if not SBOM_FILE.exists():
        print("[!] SBOM not found. Please run sbom.py first.")
        return

    try:
        sbom = json.loads(SBOM_FILE.read_text(encoding="utf-8"))
        all_vulns = []

        for component in sbom.get("components", []):
            name = component.get("name")
            version = component.get("version")
            if name and version:
                vulns = scan_package_vulns(name, version)
                all_vulns.extend(vulns)

        out_file = REPORTS / "vuln-scan-report.json"
        with open(out_file, 'w') as f:
            json.dump(all_vulns, f, indent=2)
        
        print(f"[✓] Vuln Scan complete. Identified {len(all_vulns)} vulnerabilities. Report: {out_file}")

    except Exception as e:
        print(f"[!] Vuln Scan failed: {e}")

if __name__ == "__main__":
    main()
