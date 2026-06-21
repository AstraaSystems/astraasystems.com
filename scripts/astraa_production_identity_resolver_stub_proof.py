#!/usr/bin/env python3
"""
Astraa Production Identity Resolver Stub Proof

READ-ONLY SCRIPT.

Purpose:
- Prove production identity resolver stub exists.
- Prove it fails closed by default.
- Prove it does not open customer access or connect a provider.

Does NOT:
- create sessions
- connect auth provider
- open customer access
- modify backend/auth/payment behavior
- deploy Astraa
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api.py"

REQUIRED_TEXT = [
    "ASTRAA_PRODUCTION_IDENTITY_RESOLVER_STUB_V1_START",
    "def astraa_auth_mode()",
    "def astraa_production_identity_stub_enabled()",
    "def astraa_resolve_production_identity(req)",
    "production_identity_disabled",
    "production_identity_stub_disabled",
    "production_identity_provider_not_connected",
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def check(condition, label):
    if condition:
        print("PASS:", label)
        return True
    print("FAIL:", label)
    return False


def run_dynamic_check(env_updates):
    env = os.environ.copy()
    env.update(env_updates)

    code = r'''
import api
identity, error = api.astraa_resolve_production_identity(None)
print("identity:", identity)
print("error:", error)
assert identity is None
assert isinstance(error, dict)
assert error.get("status") == "blocked"
'''

    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        env=env,
    )

    print(proc.stdout.rstrip())
    if proc.stderr:
        print("STDERR:")
        print(proc.stderr.rstrip())
    print("Exit code:", proc.returncode)
    return proc.returncode == 0


def main():
    section("ASTRAA PRODUCTION IDENTITY RESOLVER STUB PROOF")
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

    section("DEFAULT MODE FAILS CLOSED")
    all_ok = run_dynamic_check({
        "ASTRAA_AUTH_MODE": "internal_qa_dev_session",
        "ASTRAA_ENABLE_PRODUCTION_IDENTITY_STUB": "false",
    }) and all_ok

    section("PRODUCTION MODE WITHOUT ENABLE FLAG FAILS CLOSED")
    all_ok = run_dynamic_check({
        "ASTRAA_AUTH_MODE": "production_jwt",
        "ASTRAA_ENABLE_PRODUCTION_IDENTITY_STUB": "false",
    }) and all_ok

    section("PRODUCTION MODE WITH STUB ENABLED STILL FAILS CLOSED")
    all_ok = run_dynamic_check({
        "ASTRAA_AUTH_MODE": "production_jwt",
        "ASTRAA_ENABLE_PRODUCTION_IDENTITY_STUB": "true",
    }) and all_ok

    section("SUMMARY")
    if all_ok:
        print("✅ PRODUCTION IDENTITY RESOLVER STUB PROOF PASSED")
    else:
        print("❌ PRODUCTION IDENTITY RESOLVER STUB PROOF FAILED")

    section("READ-ONLY CONFIRMATION")
    print("This script did not create sessions.")
    print("This script did not connect an auth provider.")
    print("This script did not open customer access.")
    print("This script did not modify backend/auth/payment behavior.")
    print("This script did not deploy Astraa.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
