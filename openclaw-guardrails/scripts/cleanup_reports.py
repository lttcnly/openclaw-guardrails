#!/usr/bin/env python3
"""Report Cleanup: Automatically clean up old reports to prevent disk explosion.

Retention policy:
- Daily reports: Keep last 7 days
- Weekly reports: Keep last 4 weeks
- Monthly reports: Keep last 12 months
- HTML dashboards: Keep only latest 1
- JSON raw data: Keep last 14 days

Outputs:
- reports/cleanup-<ts>.json (cleanup log)
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
OUT_JSON = REPORTS / f"cleanup-{TS}.json"

# Retention policies
RETENTION = {
    # Pattern prefix -> (days_to_keep, max_files)
    "risk-score": (7, 7),  # Keep 7 days
    "summary": (7, 7),
    "skills-scan": (7, 7),
    "audit": (7, 7),
    "config-extract": (7, 7),
    "sbom": (7, 7),
    "vuln-scan": (7, 7),
    "threat-intel": (7, 7),
    "config-drift": (7, 7),
    "auto-fix": (7, 7),
    "trend-report": (30, 4),  # Keep 4 weeks
    "skills-audit": (30, 4),  # Weekly, keep 4
    "trend": (365, 12),  # Monthly trends, keep 12 months
    "dashboard": (1, 1),  # HTML dashboard, keep only latest
    "cleanup": (7, 7),  # Cleanup logs
}

# Always keep these (no cleanup)
KEEP_PATTERNS = [
    "skill-hashes-baseline.json",
    "last-alert-critical.json",
]


def get_file_age_days(file_path: Path) -> int:
    """Get file age in days."""
    try:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        age = datetime.now() - mtime
        return age.days
    except Exception:
        return 0


def should_keep(file_path: Path, pattern: str) -> Tuple[bool, str]:
    """Determine if a file should be kept based on retention policy."""
    # Always keep certain files
    if file_path.name in KEEP_PATTERNS:
        return True, "always_keep"

    # Check retention policy
    if pattern in RETENTION:
        days_to_keep, max_files = RETENTION[pattern]
        age_days = get_file_age_days(file_path)

        if age_days <= days_to_keep:
            return True, f"within_retention_{days_to_keep}d"
        else:
            return False, f"exceeded_retention_{days_to_keep}d"

    # Default: keep files less than 3 days old
    age_days = get_file_age_days(file_path)
    if age_days <= 3:
        return True, "default_short_term"
    return False, "default_cleanup"


def cleanup_reports() -> Dict[str, Any]:
    """Clean up old reports."""
    result = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scanned": 0,
        "kept": 0,
        "deleted": 0,
        "errors": 0,
        "kept_reasons": {},
        "deleted_files": [],
        "space_freed_bytes": 0,
    }

    if not REPORTS.exists():
        return result

    # Get all files
    files = sorted(REPORTS.glob("*"))
    result["scanned"] = len(files)

    # Process each file
    for file_path in files:
        if not file_path.is_file():
            continue

        # Determine pattern
        pattern = None
        for p in RETENTION.keys():
            if file_path.name.startswith(p):
                pattern = p
                break

        # Check if should keep
        keep, reason = should_keep(file_path, pattern if pattern else "unknown")

        if keep:
            result["kept"] += 1
            result["kept_reasons"][reason] = result["kept_reasons"].get(reason, 0) + 1
        else:
            # Delete file
            try:
                size = file_path.stat().st_size
                file_path.unlink()
                result["deleted"] += 1
                result["deleted_files"].append({
                    "name": file_path.name,
                    "size_bytes": size,
                    "reason": reason,
                })
                result["space_freed_bytes"] += size
            except Exception as e:
                result["errors"] += 1
                result["deleted_files"].append({
                    "name": file_path.name,
                    "error": str(e),
                })

    return result


def gen_md_report(result: Dict) -> str:
    """Generate human-readable cleanup report."""
    lines = []
    lines.append("# 🧹 Report Cleanup Summary")
    lines.append(f"**Time**: {result['time']}")
    lines.append("")

    lines.append("## Summary")
    lines.append(f"- 📁 Files Scanned: {result['scanned']}")
    lines.append(f"- ✅ Files Kept: {result['kept']}")
    lines.append(f"- 🗑️ Files Deleted: {result['deleted']}")
    lines.append(f"- ❌ Errors: {result['errors']}")
    lines.append(f"- 💾 Space Freed: {result['space_freed_bytes'] / 1024:.1f} KB")
    lines.append("")

    if result["kept_reasons"]:
        lines.append("## Kept Reasons")
        for reason, count in sorted(result["kept_reasons"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {reason}: {count}")
        lines.append("")

    if result["deleted_files"]:
        lines.append("## Deleted Files")
        for f in result["deleted_files"][:20]:  # Show first 20
            if "error" in f:
                lines.append(f"- ❌ `{f['name']}`: {f['error']}")
            else:
                size_kb = f["size_bytes"] / 1024
                lines.append(f"- 🗑️ `{f['name']}` ({size_kb:.1f} KB) - {f['reason']}")

        if len(result["deleted_files"]) > 20:
            lines.append(f"- ... and {len(result['deleted_files']) - 20} more")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by openclaw-guardrails cleanup_reports.py*")

    return "\n".join(lines)


def main() -> int:
    print("🧹 Cleaning up old reports...")

    result = cleanup_reports()

    # Save JSON
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # Save MD
    md_report = gen_md_report(result)
    OUT_MD = REPORTS / f"cleanup-{TS}.md"
    OUT_MD.write_text(md_report, encoding="utf-8")

    print(f"\n✅ Saved: {OUT_JSON}")
    print(f"✅ Saved: {OUT_MD}")

    print(f"\n📊 Summary:")
    print(f"  Scanned: {result['scanned']}")
    print(f"  Kept: {result['kept']}")
    print(f"  Deleted: {result['deleted']}")
    print(f"  Space Freed: {result['space_freed_bytes'] / 1024:.1f} KB")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
