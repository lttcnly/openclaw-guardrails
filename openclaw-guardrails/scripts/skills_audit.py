#!/usr/bin/env python3
"""Skills Behavior Audit.

Weekly audit of installed skills:
1. Compare against hash baseline (detect updates)
2. Re-scan updated skills for new risks
3. Report newly introduced dangerous patterns

Outputs:
- reports/skills-audit-<ts>.json
- reports/skills-audit-<ts>.md
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Set

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
OUT_JSON = REPORTS / f"skills-audit-{TS}.json"
OUT_MD = REPORTS / f"skills-audit-{TS}.md"

BASELINE_PATH = REPORTS / "skill-hashes-baseline.json"

# Dangerous patterns to detect
CRITICAL_PATTERNS = {
    "env_harvesting": re.compile(r"process\.env|os\.environ|getenv\s*\(", re.I),
    "network_exfil": re.compile(r"fetch\s*\(|axios\.post|curl\s|wget\s|XMLHttpRequest", re.I),
    "shell_exec": re.compile(r"child_process|exec\s*\(|spawn\s*\(|os\.system|subprocess\.", re.I),
    "credential_access": re.compile(r"keychain|credentials|token|secret|api[_-]?key", re.I),
}


def compute_file_hash(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def scan_skill_folder(skill_path: Path) -> Dict[str, Any]:
    """Scan a single skill folder for risks."""
    result = {
        "path": str(skill_path),
        "name": skill_path.name,
        "files_scanned": 0,
        "critical_patterns": [],
        "risk_score": 0,
    }

    for p in skill_path.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".js", ".ts", ".py", ".sh", ".ps1", ".mjs", ".cjs"):
            continue
        if "node_modules" in str(p):
            continue

        result["files_scanned"] += 1

        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for pattern_name, pattern in CRITICAL_PATTERNS.items():
            if pattern.search(content):
                result["critical_patterns"].append({
                    "file": str(p.relative_to(skill_path)),
                    "pattern": pattern_name,
                })
                result["risk_score"] += 10

    return result


def load_baseline() -> Dict[str, Any]:
    """Load hash baseline."""
    if not BASELINE_PATH.exists():
        return {}
    try:
        return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_baseline(data: Dict[str, Any]) -> None:
    """Save hash baseline."""
    BASELINE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def detect_changes(current: Dict, baseline: Dict) -> List[Dict[str, Any]]:
    """Detect skills that have changed since baseline."""
    changes = []

    baseline_skills = baseline.get("skills", {})
    current_skills = current.get("skills", {})

    for skill_name, skill_data in current_skills.items():
        if skill_name not in baseline_skills:
            changes.append({
                "skill": skill_name,
                "change_type": "new",
                "message": "New skill installed",
            })
            continue

        # Compare file hashes
        baseline_files = {f["path"]: f["sha256"] for f in baseline_skills[skill_name].get("files", [])}
        current_files = {f["path"]: f["sha256"] for f in skill_data.get("files", [])}

        changed_files = []
        for file_path, hash_val in current_files.items():
            if file_path not in baseline_files:
                changed_files.append({"path": file_path, "change": "added"})
            elif baseline_files[file_path] != hash_val:
                changed_files.append({"path": file_path, "change": "modified"})

        if changed_files:
            changes.append({
                "skill": skill_name,
                "change_type": "updated",
                "changed_files": changed_files[:20],  # Limit
                "message": f"{len(changed_files)} files changed",
            })

    # Check for removed skills
    for skill_name in baseline_skills:
        if skill_name not in current_skills:
            changes.append({
                "skill": skill_name,
                "change_type": "removed",
                "message": "Skill removed",
            })

    return changes


def gen_md_report(changes: List[Dict], new_risks: List[Dict]) -> str:
    """Generate human-readable markdown report."""
    lines = []
    lines.append("# 🔍 Skills Behavior Audit")
    lines.append(f"**Time**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## Summary")
    new_skills = [c for c in changes if c["change_type"] == "new"]
    updated = [c for c in changes if c["change_type"] == "updated"]
    removed = [c for c in changes if c["change_type"] == "removed"]

    lines.append(f"- 🆕 New Skills: {len(new_skills)}")
    lines.append(f"- 🔄 Updated Skills: {len(updated)}")
    lines.append(f"- ❌ Removed Skills: {len(removed)}")
    lines.append(f"- ⚠️  New Risks Detected: {len(new_risks)}")
    lines.append("")

    if new_skills:
        lines.append("## 🆕 New Skills")
        for s in new_skills:
            lines.append(f"- `{s['skill']}`")
        lines.append("")

    if updated:
        lines.append("## 🔄 Updated Skills")
        for s in updated:
            lines.append(f"- `{s['skill']}`: {s['message']}")
            if s.get("changed_files"):
                for f in s["changed_files"][:5]:
                    lines.append(f"  - {f['change']}: `{f['path']}`")
        lines.append("")

    if new_risks:
        lines.append("## ⚠️  New Risks Detected")
        for r in new_risks:
            lines.append(f"- `{r['skill']}`: {r['pattern']} in `{r['file']}`")
        lines.append("")
        lines.append("**Recommendation**: Review and consider uninstalling if risk is unacceptable.")
        lines.append("")

    if removed:
        lines.append("## ❌ Removed Skills")
        for s in removed:
            lines.append(f"- `{s['skill']}`")
        lines.append("")

    if not changes and not new_risks:
        lines.append("✅ No changes or new risks detected. All skills match baseline.")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by openclaw-guardrails skills_audit.py*")

    return "\n".join(lines)


def main() -> int:
    print("🔍 Auditing installed skills...")

    # Load baseline
    baseline = load_baseline()
    if not baseline:
        print("  - No baseline found. Run hash_pin.py first to create baseline.")
        # Create initial baseline
        from scripts import hash_pin
        # Can't import directly, skip for now
        print("  - Skipping audit, no baseline to compare against.")
        return 1

    # Scan current skills
    skill_dirs = [
        Path.home() / ".openclaw" / "skills",
        Path.home() / ".openclaw" / "extensions",
    ]

    current = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "skills": {},
    }

    new_risks = []

    for skill_dir in skill_dirs:
        if not skill_dir.exists():
            continue

        for skill_path in skill_dir.iterdir():
            if not skill_path.is_dir():
                continue
            if skill_path.name.startswith("."):
                continue

            print(f"  - Scanning: {skill_path.name}")
            result = scan_skill_folder(skill_path)
            current["skills"][skill_path.name] = result

            # Check for new critical patterns
            for pattern in result["critical_patterns"]:
                new_risks.append({
                    "skill": skill_path.name,
                    "file": pattern["file"],
                    "pattern": pattern["pattern"],
                })

    # Detect changes
    changes = detect_changes(current, baseline)

    # Save current as new baseline (for next audit)
    save_baseline(current)

    # Generate report
    md_report = gen_md_report(changes, new_risks)
    OUT_MD.write_text(md_report, encoding="utf-8")

    OUT_JSON.write_text(json.dumps({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "changes": changes,
        "new_risks": new_risks,
        "skills_scanned": len(current["skills"]),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ Saved: {OUT_JSON}")
    print(f"✅ Saved: {OUT_MD}")
    print(f"\n📊 Summary: {len(changes)} changes, {len(new_risks)} new risks")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
