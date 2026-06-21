#!/usr/bin/env python3
"""
Astraa Paid SaaS Activation Decision Guard

READ-ONLY SCRIPT.

Purpose:
- Guard the final paid SaaS production activation decision.
- Confirm all required deployment, auth, DB, secret, Host/TLS, CORS, and Moneris proof gates are explicitly acknowledged.
- Prevent accidental broad customer activation before final human/operator approval.

Does NOT:
- deploy Astraa
- start services
- modify Nginx/systemd
- request TLS certificates
- print secrets
- connect to Moneris
- run Moneris payments
- change backend/auth/payment behavior
- unlock customer access
- activate paid SaaS production mode
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from urllib.parse import urlparse


REQUIRED_FINAL_ACK_FLAGS = [
    "ASTRAA_DEPLOYED_HOST_TLS_SMOKE_PASSED",
    "ASTRAA_DEPLOYED_CORS_SMOKE_PASSED",
    "ASTRAA_DEPLOYED_AUTH_GATE_CONFIRMED",
    "ASTRAA_DEPLOYED_DB_GATE_CONFIRMED",
    "ASTRAA_DEPLOYED_SECRET_CHECK_PASSED",
    "ASTRAA_DEPLOYED_MONERIS_REGRESSION_PASSED",
    "ASTRAA_INACTIVE_ACCOUNT_BLOCK_CONFIRMED",
    "ASTRAA_DECLINED_PAYMENT_BLOCK_CONFIRMED",
    "ASTRAA_CONTROLLED_ACCOUNT_UNLOCK_CONFIRMED",
    "ASTRAA_NO_REAL_SECRETS_IN_GIT_CONFIRMED",
    "ASTRAA_FINAL_OPERATOR_APPROVAL_CONFIRMED",
]


REQUIRED_FALSE_OR_UNSET_FLAGS = [
    "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE",
]


def section(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def pass_line(message: str) -> None:
    print("[PASS]", message)


def fail_line(message: str) -> None:
    print("[FAIL]", message)


def env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}


def env_false_or_unset(name: str) -> bool:
    value = os.environ.get(name, "").strip().lower()
    return value in {"", "0", "false", "no", "n", "off"}


def validate_https_base_url(value: str) -> tuple[bool, str]:
    if not value:
        return False, "ASTRAA_DEPLOYED_BASE_URL is not set."

    parsed = urlparse(value)

    if parsed.scheme != "https":
        return False, "ASTRAA_DEPLOYED_BASE_URL must use HTTPS."

    if not parsed.netloc:
        return False, "ASTRAA_DEPLOYED_BASE_URL is missing host."

    if "*" in value:
        return False, "ASTRAA_DEPLOYED_BASE_URL must not contain wildcard."

    return True, "ASTRAA_DEPLOYED_BASE_URL is a specific HTTPS URL."


def main() -> int:
    failures: list[str] = []

    section("ASTRAA PAID SAAS ACTIVATION DECISION GUARD")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("DEPLOYED BASE URL GATE")
    base_url = os.environ.get("ASTRAA_DEPLOYED_BASE_URL", "").strip()
    ok, message = validate_https_base_url(base_url)
    if ok:
        pass_line(message)
        print("ASTRAA_DEPLOYED_BASE_URL:", base_url)
    else:
        failures.append(message)
        fail_line(message)

    section("PUBLIC LAUNCH MODE GATE")
    if env_true("ASTRAA_PUBLIC_LAUNCH_MODE"):
        pass_line("ASTRAA_PUBLIC_LAUNCH_MODE=true")
    else:
        failures.append("ASTRAA_PUBLIC_LAUNCH_MODE must be true.")
        fail_line("ASTRAA_PUBLIC_LAUNCH_MODE must be true.")

    section("DEV LOGIN DISABLED GATE")
    for flag in REQUIRED_FALSE_OR_UNSET_FLAGS:
        if env_false_or_unset(flag):
            pass_line(f"{flag} is unset or false.")
        else:
            failures.append(f"{flag} must be unset or false.")
            fail_line(f"{flag} must be unset or false.")

    section("FINAL REQUIRED ACKNOWLEDGEMENT GATES")
    for flag in REQUIRED_FINAL_ACK_FLAGS:
        if env_true(flag):
            pass_line(f"{flag}=true")
        else:
            failures.append(f"{flag} must be explicitly true before paid SaaS production activation.")
            fail_line(f"{flag} must be explicitly true before paid SaaS production activation.")

    section("SAFETY CONFIRMATION")
    print("This guard did not inspect or print secret values.")
    print("This guard only checked explicit environment acknowledgements.")
    print("This guard did not activate customer access.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not deploy Astraa.")
    print("This script did not start services.")
    print("This script did not modify Nginx/systemd.")
    print("This script did not request TLS certificates.")
    print("This script did not print secrets.")
    print("This script did not connect to Moneris.")
    print("This script did not run Moneris payments.")
    print("This script did not change backend/auth/payment behavior.")
    print("This script did not unlock customer access.")
    print("This script did not activate paid SaaS production mode.")

    section("RESULT")
    if failures:
        print("PAID SAAS ACTIVATION DECISION: BLOCKED")
        print("Paid SaaS production activation must not proceed yet.")
        print("Failures:")
        for failure in failures:
            print("-", failure)
        return 1

    print("PAID SAAS ACTIVATION DECISION: PASS")
    print("All final production activation acknowledgements are explicitly set.")
    print("Proceed only according to the controlled paid customer operating checklist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
