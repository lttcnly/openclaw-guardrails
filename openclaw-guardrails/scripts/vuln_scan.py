#!/usr/bin/env python3
"""Best-effort dependency vulnerability scan (read-only).

Cross-platform strategy:
- Node: if `npm` exists and a directory has package-lock.json -> run `npm audit --package-lock-only --json`.
- Python: if `pip-audit` exists -> run it against requirements files when present.

We do NOT auto-install scanners (to stay safe/portable). We only report what's possible.

Output:
- reports/vuln-scan-<ts>.json
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
OUT = REPORTS / f"vuln-scan-{TS}.json"

TARGET_ROOTS = [
    Path.home() / ".openclaw" / "skills",
    Path.home() / ".openclaw" / "extensions",
    ROOT,
]


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run(cmd: List[str], cwd: Path, timeout: int) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 999, "", f"{type(e).__name__}: {e}"


def find_projects() -> List[Path]:
    """Find candidate project dirs to audit (top-level under skills/extensions).

    We intentionally avoid deep recursion into node_modules.
    """
    projects: List[Path] = []
    seen = set()
    for base in TARGET_ROOTS:
        if not base.exists():
            continue
        if base == ROOT:
            projects.append(ROOT)
            continue
        for d in base.iterdir():
            if not d.is_dir():
                continue
            if d.name.startswith('.'):
                continue
            if d in seen:
                continue
            seen.add(d)
            projects.append(d)
    return projects


def npm_audit(dir_: Path) -> Dict[str, Any] | None:
    lock = dir_ / "package-lock.json"
    if not lock.exists() or not have("npm"):
        return None
    rc, out, err = run(["npm", "audit", "--package-lock-only", "--json"], cwd=dir_, timeout=60)
    return {"type": "npm", "dir": str(dir_), "rc": rc, "stdout": out[:200000], "stderr": err[:20000]}


def pip_audit_requirements(dir_: Path) -> List[Dict[str, Any]]:
    if not have("pip-audit"):
        return []
    results = []
    for fn in ("requirements.txt", "requirements-dev.txt"):
        req = dir_ / fn
        if not req.exists():
            continue
        rc, out, err = run(["pip-audit", "-r", fn, "-f", "json"], cwd=dir_, timeout=90)
        results.append({"type": "pip-audit", "dir": str(dir_), "file": fn, "rc": rc, "stdout": out[:200000], "stderr": err[:20000]})
    return results


def main() -> int:
    projects = find_projects()

    report: Dict[str, Any] = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scanners": {
            "npm": have("npm"),
            "pip_audit": have("pip-audit"),
        },
        "targets": [str(p) for p in projects],
        "results": [],
        "notes": [],
    }

    if not report["scanners"]["pip_audit"]:
        report["notes"].append("pip-audit not found; python dependency CVE scan skipped (install in a venv if desired).")

    for d in projects:
        # Node
        na = npm_audit(d)
        if na:
            report["results"].append(na)
        # Python
        report["results"].extend(pip_audit_requirements(d))

    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
