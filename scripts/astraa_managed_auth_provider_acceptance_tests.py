#!/usr/bin/env python3
"""
Astraa Managed Auth Provider Acceptance Tests

READ-ONLY / TEST SCRIPT.

Purpose:
- Acceptance-test the managed auth provider adapter skeleton.
- Confirm all provider states fail closed until a real validator/provider adapter is implemented.
- Confirm provider config checks do not expose secret values.
- Confirm no customer access is opened.

Does NOT:
- connect an auth provider
- validate real JWTs
- create users
- create sessions
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


def run_case(name, env_updates, expected_identity_source, expected_configured):
    section(name)

    env = os.environ.copy()
    env.update(env_updates)

    code = r'''
import json
import api

identity, error = api.astraa_resolve_managed_auth_identity(None)
config_status = api.astraa_managed_auth_config_status()

print(json.dumps({
    "identity": identity,
    "error": error,
    "config_status": config_status,
}, indent=2, sort_keys=True))

assert identity is None
assert isinstance(error, dict)
assert error.get("status") == "blocked"
assert config_status.get("secret_values_exposed") is False
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

    configured_text = f'"configured": {str(expected_configured).lower()}'
    passed = (
        proc.returncode == 0
        and expected_identity_source in proc.stdout
        and configured_text in proc.stdout
        and "secret_values_exposed" in proc.stdout
    )

    print("Exit code:", proc.returncode)
    print("Expected identity_source:", expected_identity_source)
    print("Expected configured:", expected_configured)
    print("Result:", "PASS" if passed else "FAIL")

    return passed


def main():
    section("ASTRAA MANAGED AUTH PROVIDER ACCEPTANCE TESTS")
    print("Mode: READ ONLY / TEST")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    cases = [
        (
            "Managed auth mode with no provider config fails closed",
            {
                "ASTRAA_AUTH_MODE": "managed_auth",
                "ASTRAA_MANAGED_AUTH_PROVIDER": "",
                "ASTRAA_AUTH_ISSUER": "",
                "ASTRAA_AUTH_AUDIENCE": "",
                "ASTRAA_AUTH_JWKS_URL": "",
                "ASTRAA_AUTH_CLIENT_ID": "",
                "ASTRAA_AUTH_CLIENT_SECRET": "",
            },
            "managed_auth_provider_not_configured",
            False,
        ),
        (
            "Managed auth mode with partial provider config fails closed",
            {
                "ASTRAA_AUTH_MODE": "managed_auth",
                "ASTRAA_MANAGED_AUTH_PROVIDER": "custom_oidc",
                "ASTRAA_AUTH_ISSUER": "https://issuer.example.invalid",
                "ASTRAA_AUTH_AUDIENCE": "",
                "ASTRAA_AUTH_JWKS_URL": "",
                "ASTRAA_AUTH_CLIENT_ID": "",
                "ASTRAA_AUTH_CLIENT_SECRET": "placeholder-secret-not-printed",
            },
            "managed_auth_provider_not_configured",
            False,
        ),
        (
            "Managed auth mode with complete placeholder config still fails closed because adapter is not implemented",
            {
                "ASTRAA_AUTH_MODE": "managed_auth",
                "ASTRAA_MANAGED_AUTH_PROVIDER": "custom_oidc",
                "ASTRAA_AUTH_ISSUER": "https://issuer.example.invalid",
                "ASTRAA_AUTH_AUDIENCE": "astraa-api",
                "ASTRAA_AUTH_JWKS_URL": "https://issuer.example.invalid/.well-known/jwks.json",
                "ASTRAA_AUTH_CLIENT_ID": "placeholder-client-id",
                "ASTRAA_AUTH_CLIENT_SECRET": "placeholder-secret-not-printed",
            },
            "managed_auth_provider_adapter_not_implemented",
            True,
        ),
        (
            "Provider OIDC mode with complete placeholder config still fails closed",
            {
                "ASTRAA_AUTH_MODE": "provider_oidc",
                "ASTRAA_MANAGED_AUTH_PROVIDER": "custom_oidc",
                "ASTRAA_AUTH_ISSUER": "https://issuer.example.invalid",
                "ASTRAA_AUTH_AUDIENCE": "astraa-api",
                "ASTRAA_AUTH_JWKS_URL": "https://issuer.example.invalid/.well-known/jwks.json",
                "ASTRAA_AUTH_CLIENT_ID": "placeholder-client-id",
                "ASTRAA_AUTH_CLIENT_SECRET": "placeholder-secret-not-printed",
            },
            "managed_auth_provider_adapter_not_implemented",
            True,
        ),
    ]

    all_ok = True
    for name, env_updates, expected_identity_source, expected_configured in cases:
        all_ok = run_case(name, env_updates, expected_identity_source, expected_configured) and all_ok

    section("SUMMARY")
    if all_ok:
        print("✅ MANAGED AUTH PROVIDER ACCEPTANCE TESTS PASSED")
    else:
        print("❌ MANAGED AUTH PROVIDER ACCEPTANCE TESTS FAILED")

    section("READ-ONLY CONFIRMATION")
    print("This script did not connect an auth provider.")
    print("This script did not validate real JWTs.")
    print("This script did not create users.")
    print("This script did not create sessions.")
    print("This script did not open customer access.")
    print("This script did not modify backend/auth/payment behavior.")
    print("This script did not deploy Astraa.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
