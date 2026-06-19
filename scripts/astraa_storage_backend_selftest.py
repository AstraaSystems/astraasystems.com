#!/usr/bin/env python3
"""
Astraa Storage Backend Self-Test

READ-ONLY SCRIPT.
Imports api.py and calls storage abstraction load wrappers.

Purpose:
- Verify ASTRAA_STORAGE_BACKEND=json works.
- Verify storage wrappers do not recurse.
- Verify usage/payment/session stores load with expected types.
- Does not save, delete, mutate, archive, migrate, or repair data.
"""

from __future__ import annotations

import os
import sys
import json
import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

# Force current backend mode for self-test.
os.environ["ASTRAA_STORAGE_BACKEND"] = "json"


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    print("=" * 96)
    print("ASTRAA STORAGE BACKEND SELF-TEST")
    print("=" * 96)
    print("Mode: READ ONLY")
    print("Working directory:", Path.cwd())
    print("ASTRAA_STORAGE_BACKEND:", os.environ.get("ASTRAA_STORAGE_BACKEND"))

    api = importlib.import_module("api")

    backend = api.astraa_storage_backend()
    print("Resolved backend:", backend)

    check(backend == "json", "Expected ASTRAA_STORAGE_BACKEND to resolve to json")

    usage_db = api.astraa_storage_load_usage_db()
    payment_db = api.astraa_storage_load_payment_db()
    sessions_db = api.astraa_storage_load_sessions_db()

    check(isinstance(usage_db, dict), "Usage DB should load as dict")
    check(isinstance(payment_db, list), "Payment DB should load as list")
    check(isinstance(sessions_db, dict), "Sessions DB should load as dict")

    print("\nLoaded store types:")
    print(json.dumps({
        "usage_db_type": type(usage_db).__name__,
        "usage_db_count": len(usage_db),
        "payment_db_type": type(payment_db).__name__,
        "payment_db_count": len(payment_db),
        "sessions_db_type": type(sessions_db).__name__,
        "sessions_db_count": len(sessions_db),
    }, indent=2, sort_keys=True))

    print("\nWrapper function names:")
    print(json.dumps({
        "usage_loader": api.astraa_storage_load_usage_db.__name__,
        "payment_loader": api.astraa_storage_load_payment_db.__name__,
        "sessions_loader": api.astraa_storage_load_sessions_db.__name__,
    }, indent=2, sort_keys=True))

    print("\n✅ Storage backend self-test passed.")
    print("READ-ONLY CONFIRMATION:")
    print("This script did not save, delete, archive, migrate, or repair any data.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\n❌ Storage backend self-test failed:")
        print(type(exc).__name__ + ":", exc)
        sys.exit(1)
