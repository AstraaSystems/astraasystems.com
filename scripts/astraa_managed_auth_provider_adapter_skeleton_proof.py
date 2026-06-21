#!/usr/bin/env python3
"""
Astraa Managed Auth Provider Adapter Skeleton Proof

READ-ONLY SCRIPT.

Purpose:
- Prove managed auth provider adapter skeleton exists.
- Prove it fails closed when provider config is missing.
- Prove it still fails closed when placeholder config is present because validation is not implemented.

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
API = ROOT / "api.py"

REQUIRED_TEXT = [
    "ASTRAA_MANAGED_AUTH_PROVIDER_ADAPTER_SKELETON_V1_START",
    "def astraa_managed_auth_provider()",
    "def astraa_managed_auth_required_env()",
    "def astraa_managed_auth_config_status()",
    "def astraa_resolve_managed_auth_identity(req)",
    "managed_auth_provider_not_configured",
    "managed_auth_provider_adapter_not_implemented",
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def check(condition, label):
    print(("PASS: " if condition else "FAIL: ") + label)
    return condition


def run_case(name, env_updates, expected_identity_source):
    section(name)

    env = os.environ.copy()
    env.update(env_updates)

    code = r'''
import json
import api

identity, error = api.astraa_resolve_managed_auth_identity(None)

print(json.dumps({
    "identity": identity,
    "error": error,
    "config_status": api.astraa_managed_auth_config_status(),
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
    section("ASTRAA MANAGED AUTH PROVIDER ADAPTER SKELETON PROOF")
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
        "Missing provider config fails closed",
        {
            "ASTRAA_AUTH_MODE": "managed_auth",
            "ASTRAA_MANAGED_AUTH_PROVIDER": "",
            "ASTRAA_AUTH_ISSUER": "",
            "ASTRAA_AUTH_AUDIENCE": "",
            "ASTRAA_AUTH_JWKS_URL": "",
            "ASTRAA_AUTH_CLIENT_ID": "",
        },
        "managed_auth_provider_not_configured",
    ) and all_ok

    all_ok = run_case(
        "Placeholder provider config still fails closed because adapter is not implemented",
        {
            "ASTRAA_AUTH_MODE": "managed_auth",
            "ASTRAA_MANAGED_AUTH_PROVIDER": "custom_oidc",
            "ASTRAA_AUTH_ISSUER": "https://issuer.example.invalid",
            "ASTRAA_AUTH_AUDIENCE": "astraa-api",
            "ASTRAA_AUTH_JWKS_URL": "https://issuer.example.invalid/.well-known/jwks.json",
            "ASTRAA_AUTH_CLIENT_ID": "placeholder-client-id",
        },
        "managed_auth_provider_adapter_not_implemented",
    ) and all_ok

    section("SUMMARY")
    if all_ok:
        print("✅ MANAGED AUTH PROVIDER ADAPTER SKELETON PROOF PASSED")
    else:
        print("❌ MANAGED AUTH PROVIDER ADAPTER SKELETON PROOF FAILED")

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
