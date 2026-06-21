#!/usr/bin/env python3
"""
Astraa Secure Secret Presence Check

READ-ONLY SCRIPT.

Purpose:
- Check whether required production/staging secrets are present.
- Never print raw secret values.
- Help prepare for production auth, managed DB, deployment, and Moneris regression.

Does NOT:
- print secret values
- create secrets
- modify environment files
- connect to services
- deploy Astraa
- change backend/auth/payment behavior
- run Moneris payments
"""

from __future__ import annotations

import os
from datetime import datetime, timezone


SECRET_GROUPS = {
    "Moneris": [
        "MONERIS_STORE_ID",
        "MONERIS_API_TOKEN",
        "MONERIS_CHECKOUT_ID",
        "MONERIS_ENV",
    ],
    "Managed DB": [
        "ASTRAA_STORAGE_BACKEND",
        "ASTRAA_MANAGED_DB_ENGINE",
        "ASTRAA_MANAGED_DB_URL",
    ],
    "Managed Auth": [
        "ASTRAA_AUTH_MODE",
        "ASTRAA_MANAGED_AUTH_PROVIDER",
        "ASTRAA_AUTH_ISSUER",
        "ASTRAA_AUTH_AUDIENCE",
        "ASTRAA_AUTH_JWKS_URL",
        "ASTRAA_AUTH_CLIENT_ID",
        "ASTRAA_AUTH_CLIENT_SECRET",
    ],
    "Session / Security": [
        "ASTRAA_SESSION_SECRET",
        "ASTRAA_PUBLIC_LAUNCH_MODE",
        "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE",
    ],
    "CORS / Deployment": [
        "ASTRAA_ALLOWED_ORIGINS",
        "BACKEND_PRELOAD_URL",
    ],
}


OPTIONAL_OR_CONTEXTUAL = {
    "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE",
    "BACKEND_PRELOAD_URL",
}


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def present(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def safe_status(name: str) -> str:
    if present(name):
        return "PRESENT"
    if name in OPTIONAL_OR_CONTEXTUAL:
        return "MISSING_OPTIONAL_OR_CONTEXTUAL"
    return "MISSING"


def main():
    section("ASTRAA SECURE SECRET PRESENCE CHECK")
    print("Mode: READ ONLY / NO SECRET VALUES PRINTED")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    all_required_present = True

    for group, names in SECRET_GROUPS.items():
        section(group)
        for name in names:
            status = safe_status(name)
            print(f"{name}: {status}")

            if status == "MISSING":
                all_required_present = False

    section("DECISION")
    if all_required_present:
        print("✅ REQUIRED SECRET PRESENCE CHECK PASSED")
        print("Required secret names appear to be present. Values were not printed.")
    else:
        print("❌ REQUIRED SECRET PRESENCE CHECK FAILED")
        print("One or more required secret names are missing. Values were not printed.")

    section("SAFETY CONFIRMATION")
    print("This script did not print secret values.")
    print("This script did not create secrets.")
    print("This script did not modify environment files.")
    print("This script did not connect to services.")
    print("This script did not deploy Astraa.")
    print("This script did not change backend/auth/payment behavior.")
    print("This script did not run Moneris payments.")

    raise SystemExit(0 if all_required_present else 1)


if __name__ == "__main__":
    main()
