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

ACTIVE_ZONE_HINTS = [
    "ASTRAA_DEV_SESSION_AUTH_V1",
    "ASTRAA_ESTIMATOR_ACCOUNT_AUTHORITY_OVERRIDE_V1",
    "ASTRAA PAYMENT VERIFICATION",
    "ASTRAA_STORAGE_ABSTRACTION_V1",
]


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

    print("\nRecommended replacement order:")
    print("1. Session functions: dev-login and auth/me path.")
    print("2. Payment DB functions: payment verification route.")
    print("3. Active Estimator usage functions around active function map lines ~4258-4447.")
    print("4. Leave shadowed/legacy definitions untouched until cleanup pass.")

    print("\nREAD-ONLY CONFIRMATION:")
    print("This script did not modify any file.")


if __name__ == "__main__":
    main()
