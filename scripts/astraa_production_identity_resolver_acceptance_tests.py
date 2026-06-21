#!/usr/bin/env python3
"""
Astraa Production Identity Resolver Acceptance Tests

READ-ONLY / TEST SCRIPT.

Purpose:
- Acceptance-test the production identity resolver stub before provider connection.
- Confirm all production auth modes fail closed until a provider adapter is implemented.
- Confirm current internal QA/dev-session behavior remains separate.

Does NOT:
- create production sessions
- connect an auth provider
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


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def run_case(name, env_updates, expected_identity_source):
    section(name)

    env = os.environ.copy()
    env.update(env_updates)

    code = r'''
import json
import api

identity, error = api.astraa_resolve_production_identity(None)

print(json.dumps({
    "identity": identity,
    "error": error,
}, indent=2, sort_keys=True))

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

    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print("STDERR:")
        print(proc.stderr.rstrip())

    passed = proc.returncode == 0 and expected_identity_source in proc.stdout

    print("Exit code:", proc.returncode)
    print("Expected identity_source:", expected_identity_source)
    print("Result:", "PASS" if passed else "FAIL")

    return passed


def main():
    section("ASTRAA PRODUCTION IDENTITY RESOLVER ACCEPTANCE TESTS")
    print("Mode: READ ONLY / TEST")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    cases = [
        (
            "Internal QA mode keeps production resolver disabled",
            {
                "ASTRAA_AUTH_MODE": "internal_qa_dev_session",
                "ASTRAA_ENABLE_PRODUCTION_IDENTITY_STUB": "false",
            },
            "production_identity_disabled",
        ),
        (
            "Production JWT mode without stub flag fails closed",
            {
                "ASTRAA_AUTH_MODE": "production_jwt",
                "ASTRAA_ENABLE_PRODUCTION_IDENTITY_STUB": "false",
            },
            "production_identity_stub_disabled",
        ),
        (
            "Production JWT mode with stub flag still fails closed because provider is not connected",
            {
                "ASTRAA_AUTH_MODE": "production_jwt",
                "ASTRAA_ENABLE_PRODUCTION_IDENTITY_STUB": "true",
            },
            "production_identity_provider_not_connected",
        ),
        (
            "Unknown auth mode fails closed",
            {
                "ASTRAA_AUTH_MODE": "unknown_mode",
                "ASTRAA_ENABLE_PRODUCTION_IDENTITY_STUB": "true",
            },
            "production_identity_disabled",
        ),
    ]

    all_ok = True
    for name, env_updates, expected in cases:
        all_ok = run_case(name, env_updates, expected) and all_ok

    section("SUMMARY")
    if all_ok:
        print("✅ PRODUCTION IDENTITY RESOLVER ACCEPTANCE TESTS PASSED")
    else:
        print("❌ PRODUCTION IDENTITY RESOLVER ACCEPTANCE TESTS FAILED")

    section("READ-ONLY CONFIRMATION")
    print("This script did not create production sessions.")
    print("This script did not connect an auth provider.")
    print("This script did not open customer access.")
    print("This script did not modify backend/auth/payment behavior.")
    print("This script did not deploy Astraa.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
