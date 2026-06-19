#!/usr/bin/env python3
"""
Astraa Storage Wrapper Adoption Plan

READ-ONLY SCRIPT.
Identifies active storage calls in api.py that should eventually route through
ASTRAA_STORAGE_ABSTRACTION_V1 wrappers.

Does not modify files.
"""

from __future__ import annotations

from pathlib import Path
import json


API_PATH = Path("api.py")

TARGET_CALLS = [
    "astraa_load_usage_db()",
    "astraa_save_usage_db(",
    "astraa_load_payment_db()",
    "astraa_save_payment_db(",
    "astraa_load_sessions_db()",
    "astraa_save_sessions_db(",
]

WRAPPER_REPLACEMENTS = {
    "astraa_load_usage_db()": "astraa_storage_load_usage_db()",
    "astraa_save_usage_db(": "astraa_storage_save_usage_db(",
    "astraa_load_payment_db()": "astraa_storage_load_payment_db()",
    "astraa_save_payment_db(": "astraa_storage_save_payment_db(",
    "astraa_load_sessions_db()": "astraa_storage_load_sessions_db()",
    "astraa_save_sessions_db(": "astraa_storage_save_sessions_db(",
}


def classify_line(line_number: int) -> str:
    """
    Coarse classification based on the active function map we already generated.
    This helps avoid blindly patching older shadowed helper blocks.
    """
    if 500 <= line_number <= 700:
        return "ACTIVE_SESSION_AUTH_ZONE"

    if 4200 <= line_number <= 4455:
        return "ACTIVE_ESTIMATOR_USAGE_HELPER_ZONE"

    if 4456 <= line_number <= 4645:
        return "ACTIVE_ESTIMATOR_ROUTE_ZONE"

    if 4650 <= line_number <= 5455:
        return "ACTIVE_PAYMENT_VERIFICATION_ZONE"

    if 900 <= line_number <= 1150:
        return "ACTIVE_PRELOAD_RECEIPT_JSONL_ZONE"

    if 1800 <= line_number <= 2105:
        return "LEGACY_OR_ACCOUNT_USAGE_ROUTE_ZONE_REVIEW"

    if line_number < 4200:
        return "EARLIER_OR_SHADOWED_ZONE_REVIEW"

    return "GENERAL_REVIEW"


def main():
    if not API_PATH.exists():
        raise SystemExit("api.py not found")

    lines = API_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()

    matches = []

    for lineno, line in enumerate(lines, 1):
        for call in TARGET_CALLS:
            if call in line:
                matches.append({
                    "line": lineno,
                    "zone": classify_line(lineno),
                    "call": call,
                    "replacement": WRAPPER_REPLACEMENTS[call],
                    "text": line.rstrip(),
                })

    print("=" * 100)
    print("ASTRAA STORAGE WRAPPER ADOPTION PLAN")
    print("=" * 100)
    print("Mode: READ ONLY")
    print("File scanned:", API_PATH)
    print("Direct storage call matches:", len(matches))

    print("\nMatches:")
    for item in matches:
        print(json.dumps(item, indent=2, sort_keys=True))

    print("\nSummary by zone:")
    zone_counts = {}
    for item in matches:
        zone_counts[item["zone"]] = zone_counts.get(item["zone"], 0) + 1

    for zone, count in sorted(zone_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"{zone}: {count}")

    print("\nRecommended replacement order:")
    print("1. ACTIVE_SESSION_AUTH_ZONE")
    print("2. ACTIVE_PAYMENT_VERIFICATION_ZONE")
    print("3. ACTIVE_ESTIMATOR_USAGE_HELPER_ZONE")
    print("4. ACTIVE_ESTIMATOR_ROUTE_ZONE")
    print("5. Leave EARLIER_OR_SHADOWED_ZONE_REVIEW untouched until cleanup pass.")

    print("\nREAD-ONLY CONFIRMATION:")
    print("This script did not modify any file.")


if __name__ == "__main__":
    main()
