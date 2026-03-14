#!/usr/bin/env python3
"""Incremental Scan: Only scan files that have changed.

Uses file system events and hash comparison to detect changes:
- watchman (macOS) - if available
- inotify (Linux) - if available  
- Fallback: hash comparison with cached baseline

Outputs:
- reports/incremental-cache.json (file hashes cache)
- reports/incremental-scan-<ts>.json (changed files only)
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Set

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M%S")
CACHE_FILE = REPORTS / "incremental-cache.json"
OUT_JSON = REPORTS / f"incremental-scan-{TS}.json"

# Paths to monitor
SCAN_PATHS = [
    Path.home() / ".openclaw" / "skills",
    Path.home() / ".openclaw" / "extensions",
]

# File types to scan
SCAN_EXTS = {".js", ".ts", ".py", ".sh", ".ps1", ".mjs", ".cjs", ".json", ".yaml", ".yml"}

# Skip directories
SKIP_DIRS = {"node_modules", "__pycache__", ".git", ".venv", "venv", "dist", "build"}


def compute_hash(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def load_cache() -> Dict[str, str]:
    """Load cached file hashes."""
    if not CACHE_FILE.exists():
        return {}
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        return data.get("files", {})
    except Exception:
        return {}


def save_cache(file_hashes: Dict[str, str]) -> None:
    """Save file hashes cache."""
    CACHE_FILE.write_text(json.dumps({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "files": file_hashes,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def scan_paths() -> Dict[str, str]:
    """Scan all paths and compute file hashes."""
    current_hashes = {}

    for base_path in SCAN_PATHS:
        if not base_path.exists():
            continue

        for file_path in base_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip directories
            if any(skip in str(file_path) for skip in SKIP_DIRS):
                continue

            # Check extension
            if file_path.suffix.lower() not in SCAN_EXTS:
                continue

            # Compute hash
            file_hash = compute_hash(file_path)
            if file_hash:
                rel_path = str(file_path.relative_to(Path.home()))
                current_hashes[rel_path] = file_hash

    return current_hashes


def detect_changes(old_hashes: Dict[str, str], new_hashes: Dict[str, str]) -> Dict[str, Any]:
    """Detect file changes between two hash sets."""
    old_set = set(old_hashes.keys())
    new_set = set(new_hashes.keys())

    added = new_set - old_set
    removed = old_set - new_set
    common = old_set & new_set

    modified = set()
    for path in common:
        if old_hashes[path] != new_hashes[path]:
            modified.add(path)

    return {
        "added": sorted(list(added)),
        "removed": sorted(list(removed)),
        "modified": sorted(list(modified)),
        "unchanged_count": len(common) - len(modified),
    }


def main() -> int:
    print("🔄 Running incremental scan...")

    # Load cached hashes
    print("  - Loading cached hashes...")
    old_hashes = load_cache()
    print(f"    Cached files: {len(old_hashes)}")

    # Scan current state
    print("  - Scanning current files...")
    new_hashes = scan_paths()
    print(f"    Current files: {len(new_hashes)}")

    # Detect changes
    print("  - Detecting changes...")
    changes = detect_changes(old_hashes, new_hashes)

    # Save new cache
    save_cache(new_hashes)

    # Generate report
    report = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "changes": changes,
        "summary": {
            "added": len(changes["added"]),
            "removed": len(changes["removed"]),
            "modified": len(changes["modified"]),
            "unchanged": changes["unchanged_count"],
            "total_current": len(new_hashes),
        }
    }

    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ Saved: {OUT_JSON}")
    print(f"✅ Cache updated: {CACHE_FILE}")

    print(f"\n📊 Summary:")
    print(f"  Added: {len(changes['added'])}")
    print(f"  Removed: {len(changes['removed'])}")
    print(f"  Modified: {len(changes['modified'])}")
    print(f"  Unchanged: {changes['unchanged_count']}")

    # If there are changes, trigger full scan
    if changes["added"] or changes["modified"]:
        print("\n⚠️  Changes detected! Running full skills scan...")
        import subprocess
        result = subprocess.run(
            ["python3", str(ROOT / "scripts" / "skills_scan.py")],
            capture_output=True,
            text=True,
            timeout=300,
        )
        print(result.stdout[-500:] if result.stdout else "")
        if result.stderr:
            print(result.stderr[-500:])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
