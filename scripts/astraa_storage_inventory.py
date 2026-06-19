#!/usr/bin/env python3
"""
Astraa Storage Inventory

READ-ONLY SCRIPT.
Scans api.py for local runtime storage references before adding a storage abstraction layer.
Does not modify files.
"""

from __future__ import annotations

from pathlib import Path
import re
import json


API_PATH = Path("api.py")

PATTERNS = [
    "astraa_usage_db.json",
    "astraa_payment_db.json",
    "astraa_sessions.json",
    "preloads.jsonl",
    "payments.jsonl",
    "append_jsonl",
    "load_usage",
    "save_usage",
    "load_payment",
    "save_payment",
    "load_sessions",
    "save_sessions",
    "PAYMENTS_FILE",
    "PRELOADS_FILE",
    "USAGE",
    "PAYMENT",
    "SESSIONS",
]


def main():
    if not API_PATH.exists():
        raise SystemExit("api.py not found")

    lines = API_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()

    results = []

    for lineno, line in enumerate(lines, 1):
        matched = [pattern for pattern in PATTERNS if pattern.lower() in line.lower()]
        if matched:
            results.append({
                "line": lineno,
                "matched": matched,
                "text": line.rstrip()
            })

    print("=" * 90)
    print("ASTRAA STORAGE INVENTORY")
    print("=" * 90)
    print("Mode: READ ONLY")
    print("File scanned:", API_PATH)
    print("Matches:", len(results))

    print("\nMatches by line:")
    for item in results:
        print(json.dumps(item, indent=2, sort_keys=True))

    print("\nSummary by pattern:")
    counts = {}
    for item in results:
        for pattern in item["matched"]:
            counts[pattern] = counts.get(pattern, 0) + 1

    for pattern, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"{pattern}: {count}")

    print("\nREAD-ONLY CONFIRMATION:")
    print("This script did not modify any file.")


if __name__ == "__main__":
    main()
