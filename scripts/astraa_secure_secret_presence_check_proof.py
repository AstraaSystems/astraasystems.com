#!/usr/bin/env python3
"""
Astraa Secure Secret Presence Check Proof

READ-ONLY SCRIPT.

Purpose:
- Prove the secure secret presence checker runs without exposing secret values.
- Prove missing secrets fail safely.
- Prove placeholder complete env passes without printing values.

Does NOT:
- print real secret values
- create secrets
- modify environment files
- connect to services
- deploy Astraa
- run Moneris payments
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


PLACEHOLDER_ENV = {
    "MONERIS_STORE_ID": "present-not-printed",
    "MONERIS_API_TOKEN": "present-not-printed",
    "MONERIS_CHECKOUT_ID": "present-not-printed",
    "MONERIS_ENV": "prod",
    "ASTRAA_STORAGE_BACKEND": "json",
    "ASTRAA_MANAGED_DB_ENGINE": "postgres",
    "ASTRAA_MANAGED_DB_URL": "present-not-printed",
    "ASTRAA_AUTH_MODE": "managed_auth",
    "ASTRAA_MANAGED_AUTH_PROVIDER": "custom_oidc",
    "ASTRAA_AUTH_ISSUER": "present-not-printed",
    "ASTRAA_AUTH_AUDIENCE": "present-not-printed",
    "ASTRAA_AUTH_JWKS_URL": "present-not-printed",
    "ASTRAA_AUTH_CLIENT_ID": "present-not-printed",
    "ASTRAA_AUTH_CLIENT_SECRET": "present-not-printed",
    "ASTRAA_SESSION_SECRET": "present-not-printed",
    "ASTRAA_PUBLIC_LAUNCH_MODE": "true",
    "ASTRAA_ALLOWED_ORIGINS": "present-not-printed",
}


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def run_case(name, env_updates, expect_success):
    section(name)

    env = os.environ.copy()
    env.update(env_updates)

    proc = subprocess.run(
        [sys.executable, "scripts/astraa_secure_secret_presence_check.py"],
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

    contains_placeholder_secret = "present-not-printed" in proc.stdout
    success_matches = (proc.returncode == 0) == expect_success

    passed = success_matches and not contains_placeholder_secret

    print("Exit code:", proc.returncode)
    print("Expected success:", expect_success)
    print("Secret values exposed:", contains_placeholder_secret)
    print("Result:", "PASS" if passed else "FAIL")

    return passed


def main():
    section("ASTRAA SECURE SECRET PRESENCE CHECK PROOF")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    all_ok = True

    all_ok = run_case(
        "Missing secrets fail safely",
        {
            "MONERIS_STORE_ID": "",
            "MONERIS_API_TOKEN": "",
            "MONERIS_CHECKOUT_ID": "",
            "MONERIS_ENV": "",
            "ASTRAA_STORAGE_BACKEND": "",
            "ASTRAA_MANAGED_DB_ENGINE": "",
            "ASTRAA_MANAGED_DB_URL": "",
            "ASTRAA_AUTH_MODE": "",
            "ASTRAA_MANAGED_AUTH_PROVIDER": "",
            "ASTRAA_AUTH_ISSUER": "",
            "ASTRAA_AUTH_AUDIENCE": "",
            "ASTRAA_AUTH_JWKS_URL": "",
            "ASTRAA_AUTH_CLIENT_ID": "",
            "ASTRAA_AUTH_CLIENT_SECRET": "",
            "ASTRAA_SESSION_SECRET": "",
            "ASTRAA_PUBLIC_LAUNCH_MODE": "",
            "ASTRAA_ALLOWED_ORIGINS": "",
        },
        False,
    ) and all_ok

    all_ok = run_case(
        "Placeholder complete env passes without exposing values",
        PLACEHOLDER_ENV,
        True,
    ) and all_ok

    section("SUMMARY")
    if all_ok:
        print("✅ SECURE SECRET PRESENCE CHECK PROOF PASSED")
    else:
        print("❌ SECURE SECRET PRESENCE CHECK PROOF FAILED")

    section("READ-ONLY CONFIRMATION")
    print("This script did not print real secret values.")
    print("This script did not create secrets.")
    print("This script did not modify environment files.")
    print("This script did not connect to services.")
    print("This script did not deploy Astraa.")
    print("This script did not run Moneris payments.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
