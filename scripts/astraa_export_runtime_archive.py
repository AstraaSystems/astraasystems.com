#!/usr/bin/env python3
"""
Astraa Runtime Archive Export

SAFE EXPORT SCRIPT.
This script copies runtime data into a timestamped archive folder.

It does NOT:
- delete original files
- modify original files
- repair records
- migrate records
- change active runtime state

Output:
- SAFE_SNAPSHOTS/runtime_archive_YYYYMMDD_HHMMSS/
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(".")
SOURCE_FILES = [
    ROOT / "astraa_data" / "astraa_usage_db.json",
    ROOT / "astraa_data" / "astraa_payment_db.json",
    ROOT / "astraa_data" / "astraa_sessions.json",
    ROOT / "preloads.jsonl",
    ROOT / "payments.jsonl",
]

SNAPSHOT_ROOT = ROOT / "SAFE_SNAPSHOTS"


def now_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def safe_copy_file(source: Path, dest_dir: Path):
    if not source.exists():
        return {
            "source": str(source),
            "copied": False,
            "reason": "source file not found"
        }

    target = dest_dir / source.name

    if source.parent.name == "astraa_data":
        target = dest_dir / f"astraa_data__{source.name}"

    shutil.copy2(source, target)

    return {
        "source": str(source),
        "target": str(target),
        "copied": True,
        "bytes": target.stat().st_size
    }


def main():
    SNAPSHOT_ROOT.mkdir(exist_ok=True)

    archive_dir = SNAPSHOT_ROOT / f"runtime_archive_{now_stamp()}"
    archive_dir.mkdir(parents=True, exist_ok=False)

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "copy_only_no_delete_no_mutation",
        "archive_dir": str(archive_dir),
        "files": []
    }

    for source in SOURCE_FILES:
        manifest["files"].append(safe_copy_file(source, archive_dir))

    manifest_path = archive_dir / "archive_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print("✅ Runtime archive export complete")
    print("Archive directory:", archive_dir)
    print("Manifest:", manifest_path)
    print()
    print("Copied files:")
    for item in manifest["files"]:
        print(json.dumps(item, indent=2, sort_keys=True))
    print()
    print("SAFETY CONFIRMATION:")
    print("Original runtime files were not deleted or modified.")


if __name__ == "__main__":
    main()
