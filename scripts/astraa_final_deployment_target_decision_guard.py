#!/usr/bin/env python3
"""
Astraa Final Deployment Target Decision Guard

READ-ONLY SCRIPT.

Purpose:
- Guard the transition from local production-readiness proofs to real deployed-runtime work.
- Confirm final deployment target decisions are explicitly represented before live Host/TLS smoke checks.
- Keep host/subdomain/runtime/CORS/secret-source decisions separate from deployment mutation.

Does NOT:
- deploy Astraa
- start services
- modify Nginx/systemd
- request TLS certificates
- print secrets
- connect to production host
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


REQUIRED_URL_FLAGS = [
    "ASTRAA_PUBLIC_SITE_ORIGIN",
    "ASTRAA_DEPLOYED_BASE_URL",
    "ASTRAA_CORS_TEST_ORIGIN",
]


REQUIRED_TEXT_FLAGS = [
    "ASTRAA_DEPLOYMENT_RUNTIME",
    "ASTRAA_TLS_TERMINATION_PATH",
    "ASTRAA_PRODUCTION_SECRET_SOURCE",
    "ASTRAA_PRODUCTION_DB_TARGET",
    "ASTRAA_PRODUCTION_AUTH_PROVIDER",
]


REQUIRED_TRUE_FLAGS = [
    "ASTRAA_PUBLIC_LAUNCH_MODE",
    "ASTRAA_FINAL_DEPLOYMENT_TARGET_CONFIRMED",
]


REQUIRED_FALSE_OR_UNSET_FLAGS = [
    "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE",
]


ALLOWED_RUNTIME_HINTS = {
    "gunicorn",
    "wsgi",
    "managed",
    "container",
    "app-service",
    "render",
    "railway",
    "fly",
    "azure",
    "aws",
    "gcp",
    "vercel",
    "nginx",
}


ALLOWED_SECRET_SOURCE_HINTS = {
    "environment",
    "secret-manager",
    "key-vault",
    "vault",
    "managed-secret",
    "host-env",
}


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


def validate_https_url(name: str, value: str) -> tuple[bool, str]:
    if not value:
        return False, f"{name} is not set."

    parsed = urlparse(value)

    if parsed.scheme != "https":
        return False, f"{name} must use HTTPS."

    if not parsed.netloc:
        return False, f"{name} is missing host."

    if "*" in value:
        return False, f"{name} must not contain wildcard."

    return True, f"{name} is a specific HTTPS URL."


def contains_hint(value: str, hints: set[str]) -> bool:
    normalized = value.strip().lower()
    return any(hint in normalized for hint in hints)


def main() -> int:
    failures: list[str] = []

    section("ASTRAA FINAL DEPLOYMENT TARGET DECISION GUARD")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("HTTPS URL DECISION GATES")
    for flag in REQUIRED_URL_FLAGS:
        value = os.environ.get(flag, "").strip()
        ok, message = validate_https_url(flag, value)
        if ok:
            pass_line(message)
            print(f"{flag}:", value)
        else:
            failures.append(message)
            fail_line(message)

    section("DEPLOYMENT TARGET TEXT DECISION GATES")
    for flag in REQUIRED_TEXT_FLAGS:
        value = os.environ.get(flag, "").strip()
        if value:
            pass_line(f"{flag} is set.")
            print(f"{flag}:", value)
        else:
            failures.append(f"{flag} must be set before deployed smoke proof.")
            fail_line(f"{flag} must be set before deployed smoke proof.")

    section("RUNTIME SANITY CHECK")
    runtime_value = os.environ.get("ASTRAA_DEPLOYMENT_RUNTIME", "").strip()
    if runtime_value and contains_hint(runtime_value, ALLOWED_RUNTIME_HINTS):
        pass_line("Deployment runtime looks production-style.")
    elif runtime_value:
        warn_line("Deployment runtime is set but does not match common production runtime hints.")
        warn_line("This may still be valid, but manually verify it is not Flask dev server.")
    else:
        failures.append("Deployment runtime is missing.")
        fail_line("Deployment runtime is missing.")

    section("SECRET SOURCE SANITY CHECK")
    secret_source = os.environ.get("ASTRAA_PRODUCTION_SECRET_SOURCE", "").strip()
    if secret_source and contains_hint(secret_source, ALLOWED_SECRET_SOURCE_HINTS):
        pass_line("Production secret source looks external/managed.")
    elif secret_source:
        warn_line("Production secret source is set but does not match common secret-source hints.")
        warn_line("Manually verify real secrets are not stored in git-tracked files.")
    else:
        failures.append("Production secret source is missing.")
        fail_line("Production secret source is missing.")

    section("PUBLIC MODE AND DEV LOGIN GATES")
    for flag in REQUIRED_TRUE_FLAGS:
        if env_true(flag):
            pass_line(f"{flag}=true")
        else:
            failures.append(f"{flag} must be explicitly true.")
            fail_line(f"{flag} must be explicitly true.")

    for flag in REQUIRED_FALSE_OR_UNSET_FLAGS:
        if env_false_or_unset(flag):
            pass_line(f"{flag} is unset or false.")
        else:
            failures.append(f"{flag} must be unset or false.")
            fail_line(f"{flag} must be unset or false.")

    section("SAFETY CONFIRMATION")
    print("This guard did not inspect or print secret values.")
    print("This guard only checked explicit deployment target decisions.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not deploy Astraa.")
    print("This script did not start services.")
    print("This script did not modify Nginx/systemd.")
    print("This script did not request TLS certificates.")
    print("This script did not print secrets.")
    print("This script did not connect to production host.")
    print("This script did not connect to Moneris.")
    print("This script did not run Moneris payments.")
    print("This script did not change backend/auth/payment behavior.")
    print("This script did not unlock customer access.")
    print("This script did not activate paid SaaS production mode.")

    section("RESULT")
    if failures:
        print("FINAL DEPLOYMENT TARGET DECISION: BLOCKED")
        print("Do not run deployed Host/TLS or CORS smoke proof yet.")
        print("Failures:")
        for failure in failures:
            print("-", failure)
        return 1

    print("FINAL DEPLOYMENT TARGET DECISION: PASS")
    print("Final deployment target decisions are explicitly represented.")
    print("Next step: run deployed Host/TLS smoke proof against the final HTTPS URL.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
