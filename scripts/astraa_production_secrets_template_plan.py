#!/usr/bin/env python3
"""
Astraa Production Secrets Template Plan

READ-ONLY SCRIPT.

Purpose:
- Define production environment variables and secret placeholders.
- Prepare secure deployment environment planning.
- Avoid committing real secrets.

Does NOT:
- print actual environment variable values
- create .env files
- modify files
- change secrets
- deploy Astraa
"""

from __future__ import annotations

from datetime import datetime, timezone


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def print_list(items):
    for item in items:
        print("-", item)


def main():
    section("ASTRAA PRODUCTION SECRETS TEMPLATE PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("NON-SECRET PRODUCTION FLAGS")
    print_list([
        "ASTRAA_PUBLIC_LAUNCH_MODE=true",
        "ASTRAA_REQUEST_GUARD_ENABLED=true",
        "ASTRAA_STORAGE_BACKEND=json initially for controlled staging only; managed DB later.",
        "ASTRAA_ALLOWED_ORIGINS=https://astraasystems.com,https://www.astraasystems.com",
        "ASTRAA_ALLOW_LOCALHOST_CORS=false",
        "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE must remain unset or false in production.",
        "MONERIS_ENV=prod",
        "ASTRAA_TEST_AMOUNT=2.00 only while controlled Moneris proof pricing remains intentional.",
    ])

    section("SECRET PLACEHOLDERS")
    print_list([
        "MONERIS_STORE_ID=REPLACE_WITH_SECURE_SECRET",
        "MONERIS_API_TOKEN=REPLACE_WITH_SECURE_SECRET",
        "MONERIS_CHECKOUT_ID=REPLACE_WITH_SECURE_SECRET",
        "Future DB URL/password should come from secret manager, not git.",
        "Future auth provider client secret should come from secret manager, not git.",
    ])

    section("SAFE ENV TEMPLATE PREVIEW")
    print("""
# Astraa production environment template — placeholders only.
# Do not commit real secrets.

ASTRAA_PUBLIC_LAUNCH_MODE=true
ASTRAA_REQUEST_GUARD_ENABLED=true
ASTRAA_STORAGE_BACKEND=json
ASTRAA_ALLOWED_ORIGINS=https://astraasystems.com,https://www.astraasystems.com
ASTRAA_ALLOW_LOCALHOST_CORS=false

MONERIS_ENV=prod
MONERIS_STORE_ID=REPLACE_WITH_SECURE_SECRET
MONERIS_API_TOKEN=REPLACE_WITH_SECURE_SECRET
MONERIS_CHECKOUT_ID=REPLACE_WITH_SECURE_SECRET
ASTRAA_TEST_AMOUNT=2.00
""".strip())

    section("SECRET HANDLING RULES")
    print_list([
        "Never commit real Moneris credentials.",
        "Never expose secrets in frontend JavaScript.",
        "Never print full secret values in logs.",
        "Use deployment host environment, secure env file, or managed secret store.",
        "Restrict permissions on server env files.",
        "Rotate secrets if any real value is accidentally committed or exposed.",
    ])

    section("NEXT SAFE STEP")
    print("Create a guarded local template writer that only writes placeholder files under deployment_templates/ if explicitly enabled.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not print actual environment values.")
    print("This script did not create .env files.")
    print("This script did not modify files.")
    print("This script did not change secrets.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
