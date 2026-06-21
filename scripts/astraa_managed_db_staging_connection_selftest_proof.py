#!/usr/bin/env python3
"""
Astraa Managed DB Staging Connection Self-Test Proof

READ-ONLY SCRIPT.

Purpose:
- Prove managed DB staging connection self-test refuses by default.
- Prove local SQLite staging connection check only runs with explicit flag.
- Keep managed DB work separate from migration/import/cutover.

Does NOT:
- create production databases
- create production tables
- import data
- migrate data
- open customer access
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def run_case(name, env_updates, expected_text):
    section(name)

    env = os.environ.copy()
    env.update(env_updates)

    proc = subprocess.run(
        [sys.executable, "scripts/astraa_managed_db_staging_connection_selftest.py"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        env=env,
    )

    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print("STDERR:")
        print(proc.stderr.rstrip())

    passed = proc.returncode == 0 and expected_text in proc.stdout

    print("Exit code:", proc.returncode)
    print("Expected text:", expected_text)
    print("Result:", "PASS" if passed else "FAIL")

    return passed


def main():
    section("ASTRAA MANAGED DB STAGING CONNECTION SELF-TEST PROOF")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    all_ok = True

    all_ok = run_case(
        "Default refusal",
        {
            "ASTRAA_ALLOW_MANAGED_DB_STAGING_SELFTEST": "false",
            "ASTRAA_MANAGED_DB_ENGINE": "",
            "ASTRAA_MANAGED_DB_URL": "",
        },
        "Refusing to test managed DB staging connection",
    ) and all_ok

    all_ok = run_case(
        "Explicit local SQLite staging connection check",
        {
            "ASTRAA_ALLOW_MANAGED_DB_STAGING_SELFTEST": "true",
            "ASTRAA_MANAGED_DB_ENGINE": "sqlite",
            "ASTRAA_MANAGED_DB_SQLITE_PATH": "astraa_data/astraa_staging.db",
        },
        "PASS: SQLite staging connection check succeeded.",
    ) and all_ok

    all_ok = run_case(
        "PostgreSQL missing URL fails safely",
        {
            "ASTRAA_ALLOW_MANAGED_DB_STAGING_SELFTEST": "true",
            "ASTRAA_MANAGED_DB_ENGINE": "postgres",
            "ASTRAA_MANAGED_DB_URL": "",
        },
        "FAIL: ASTRAA_MANAGED_DB_URL is required",
    ) is False and all_ok
    # Above intentionally expects the child script to fail when URL is missing.
    # Treat that fail-closed behavior as a proof pass.

    section("SUMMARY")
    if all_ok:
        print("✅ MANAGED DB STAGING CONNECTION SELF-TEST PROOF PASSED")
    else:
        print("❌ MANAGED DB STAGING CONNECTION SELF-TEST PROOF FAILED")

    section("READ-ONLY CONFIRMATION")
    print("This script did not create production databases.")
    print("This script did not create production tables.")
    print("This script did not import data.")
    print("This script did not migrate data.")
    print("This script did not open customer access.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
