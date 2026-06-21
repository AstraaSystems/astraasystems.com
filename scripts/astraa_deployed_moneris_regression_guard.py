#!/usr/bin/env python3
"""
Astraa Deployed Moneris Regression Guard

READ-ONLY SCRIPT.

Purpose:
- Guard the deployed Moneris regression lane.
- Confirm required deployment preconditions are explicitly represented before any live/controlled payment regression.
- Prevent accidental payment testing before Host/TLS, CORS, auth, DB, and secret gates are acknowledged.

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
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from urllib.parse import urlparse


REQUIRED_ACK_FLAGS = [
    "ASTRAA_DEPLOYED_HOST_TLS_SMOKE_PASSED",
    "ASTRAA_DEPLOYED_CORS_SMOKE_PASSED",
    "ASTRAA_DEPLOYED_AUTH_GATE_CONFIRMED",
    "ASTRAA_DEPLOYED_DB_GATE_CONFIRMED",
    "ASTRAA_DEPLOYED_SECRET_CHECK_PASSED",
    "ASTRAA_MONERIS_CONTROLLED_TEST_ACCOUNT_CONFIRMED",
]


REQUIRED_FALSE_FLAGS = [
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


def warn_line(message: str) -> None:
    print("[WARN]", message)


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

    section("ASTRAA DEPLOYED MONERIS REGRESSION GUARD")
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

    section("REQUIRED ACKNOWLEDGEMENT GATES")
    for flag in REQUIRED_ACK_FLAGS:
        if env_true(flag):
            pass_line(f"{flag}=true")
        else:
            failures.append(f"{flag} must be explicitly true before deployed Moneris regression.")
            fail_line(f"{flag} must be explicitly true before deployed Moneris regression.")

    section("REQUIRED DISABLED FLAGS")
    for flag in REQUIRED_FALSE_FLAGS:
        if env_false_or_unset(flag):
            pass_line(f"{flag} is unset or false.")
        else:
            failures.append(f"{flag} must be unset or false before deployed Moneris regression.")
            fail_line(f"{flag} must be unset or false before deployed Moneris regression.")

    section("PUBLIC LAUNCH MODE GATE")
    if env_true("ASTRAA_PUBLIC_LAUNCH_MODE"):
        pass_line("ASTRAA_PUBLIC_LAUNCH_MODE=true")
    else:
        failures.append("ASTRAA_PUBLIC_LAUNCH_MODE must be true before deployed Moneris regression.")
        fail_line("ASTRAA_PUBLIC_LAUNCH_MODE must be true before deployed Moneris regression.")

    section("SAFETY CONFIRMATION")
    print("This guard did not inspect or print secret values.")
    print("This guard only checked explicit environment acknowledgements.")

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

    section("RESULT")
    if failures:
        print("DEPLOYED MONERIS REGRESSION GUARD: BLOCKED")
        print("Actual deployed Moneris regression must not run yet.")
        print("Failures:")
        for failure in failures:
            print("-", failure)
        return 1

    print("DEPLOYED MONERIS REGRESSION GUARD: PASS")
    print("All explicit preconditions are acknowledged.")
    print("Proceed only with one controlled deployed Moneris regression using the dedicated controlled account.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
