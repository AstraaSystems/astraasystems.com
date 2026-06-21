#!/usr/bin/env python3
"""
Astraa Managed DB Adapter Skeleton Proof

READ-ONLY SCRIPT.

Purpose:
- Prove managed DB adapter skeleton exists.
- Prove JSON/local storage remains the safe default.
- Prove managed DB adapter load/save stubs fail closed.
- Prove no secret values are exposed.
- Import api.py with safe JSON storage first, because Core OS storage currently supports json only at import time.

Does NOT:
- connect to managed DB
- create tables
- create indexes
- import data
- migrate data
- open customer access
- modify backend/auth/payment behavior
- deploy Astraa
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api.py"

REQUIRED_TEXT = [
    "ASTRAA_MANAGED_DB_ADAPTER_SKELETON_V1_START",
    "def astraa_storage_backend()",
    "def astraa_managed_db_adapter_selected()",
    "def astraa_managed_db_required_env()",
    "def astraa_managed_db_config_status()",
    "def astraa_managed_db_adapter_blocked(operation, store_name)",
    "def astraa_managed_db_load_store_stub(store_name)",
    "def astraa_managed_db_save_store_stub(store_name, data)",
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def check(condition, label):
    print(("PASS: " if condition else "FAIL: ") + label)
    return condition


def run_case(name, env_updates, expected_text):
    section(name)

    # Important:
    # api.py initializes some Core OS storage at import time.
    # That storage currently supports json only.
    # So the subprocess imports api with ASTRAA_STORAGE_BACKEND=json first,
    # then applies managed DB test env values after import.
    safe_env = os.environ.copy()
    safe_env["ASTRAA_STORAGE_BACKEND"] = "json"

    env_updates_json = json.dumps(env_updates)

    code = r'''
import json
import os

TEST_ENV_UPDATES = json.loads(os.environ["ASTRAA_TEST_ENV_UPDATES_JSON"])

# Import api.py with safe JSON storage first because api.py currently initializes
# Core OS storage at import time, and Core OS storage supports only json today.
os.environ["ASTRAA_STORAGE_BACKEND"] = "json"
import api

# After import, apply the test case environment dynamically so the managed DB
# adapter skeleton can be tested without triggering import-time Core OS failure.
for key, value in TEST_ENV_UPDATES.items():
    os.environ[key] = value

status = api.astraa_managed_db_config_status()
print(json.dumps(status, indent=2, sort_keys=True))

try:
    api.astraa_managed_db_load_store_stub("sessions")
except RuntimeError as exc:
    print("load_stub_error:", str(exc))

try:
    api.astraa_managed_db_save_store_stub("sessions", {})
except RuntimeError as exc:
    print("save_stub_error:", str(exc))
'''

    safe_env["ASTRAA_TEST_ENV_UPDATES_JSON"] = env_updates_json

    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        env=safe_env,
    )

    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print("STDERR:")
        print(proc.stderr.rstrip())

    passed = (
        proc.returncode == 0
        and expected_text in proc.stdout
        and '"secret_values_exposed": false' in proc.stdout
        and "load_stub_error:" in proc.stdout
        and "save_stub_error:" in proc.stdout
    )

    print("Exit code:", proc.returncode)
    print("Expected text:", expected_text)
    print("Result:", "PASS" if passed else "FAIL")

    return passed


def main():
    section("ASTRAA MANAGED DB ADAPTER SKELETON PROOF")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    all_ok = True

    section("STATIC CHECKS")
    text = API.read_text(encoding="utf-8", errors="ignore")

    for required in REQUIRED_TEXT:
        all_ok = check(required in text, f"Found {required}") and all_ok

    section("PY COMPILE")
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", "api.py"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip())
    all_ok = check(proc.returncode == 0, "api.py compiles") and all_ok

    all_ok = run_case(
        "JSON default remains safe",
        {
            "ASTRAA_STORAGE_BACKEND": "json",
            "ASTRAA_MANAGED_DB_ENGINE": "",
            "ASTRAA_MANAGED_DB_URL": "",
        },
        '"storage_backend": "json"',
    ) and all_ok

    all_ok = run_case(
        "Managed DB selected but missing config remains blocked",
        {
            "ASTRAA_STORAGE_BACKEND": "managed_db",
            "ASTRAA_MANAGED_DB_ENGINE": "",
            "ASTRAA_MANAGED_DB_URL": "",
        },
        "Managed DB adapter skeleton is present but real managed DB storage operations are not implemented yet",
    ) and all_ok

    all_ok = run_case(
        "Managed DB selected with placeholder config still blocks operations",
        {
            "ASTRAA_STORAGE_BACKEND": "managed_db",
            "ASTRAA_MANAGED_DB_ENGINE": "postgres",
            "ASTRAA_MANAGED_DB_URL": "postgresql://user:secret@example.invalid/astraa_staging",
        },
        '"configured": true',
    ) and all_ok

    section("SUMMARY")
    if all_ok:
        print("✅ MANAGED DB ADAPTER SKELETON PROOF PASSED")
    else:
        print("❌ MANAGED DB ADAPTER SKELETON PROOF FAILED")

    section("READ-ONLY CONFIRMATION")
    print("This script did not connect to managed DB.")
    print("This script did not create tables.")
    print("This script did not create indexes.")
    print("This script did not import data.")
    print("This script did not migrate data.")
    print("This script did not open customer access.")
    print("This script did not modify backend/auth/payment behavior.")
    print("This script did not deploy Astraa.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
