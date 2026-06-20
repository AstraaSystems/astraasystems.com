#!/usr/bin/env python3
"""
Astraa CORS Domain Lock Plan

READ-ONLY SCRIPT.

Purpose:
- Plan production CORS/domain restrictions before patching api.py.
- Preserve local/internal QA access while preparing public launch domain safety.

Does NOT:
- modify api.py
- change CORS behavior
- change routes
- create deployment config
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
    section("ASTRAA CORS DOMAIN LOCK PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("GOAL")
    print_list([
        "Replace broad Access-Control-Allow-Origin behavior with explicit Astraa allowed origins before public launch.",
        "Preserve localhost/internal QA access through explicit development flags.",
        "Avoid breaking Moneris/payment, Estimator, auth, and staging proof flows.",
    ])

    section("PROPOSED ALLOWED PUBLIC ORIGINS")
    print_list([
        "https://astraasystems.com",
        "https://www.astraasystems.com",
        "Future staging domain if used, e.g. https://staging.astraasystems.com",
    ])

    section("PROPOSED INTERNAL QA ORIGINS")
    print_list([
        "http://localhost:5000",
        "http://localhost:8000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:8000",
        "Local LAN origin only if explicitly enabled for internal testing.",
    ])

    section("PROPOSED ENV FLAGS")
    print_list([
        "ASTRAA_PUBLIC_LAUNCH_MODE=true enables strict CORS behavior.",
        "ASTRAA_ALLOWED_ORIGINS can define comma-separated production origins.",
        "ASTRAA_ALLOW_LOCALHOST_CORS=true allows localhost during internal QA.",
        "Default in public launch mode should deny unknown origins.",
    ])

    section("ROUTES TO PROTECT")
    print_list([
        "/api/auth/dev-login",
        "/api/auth/me",
        "/api/payment/verify-moneris-receipt",
        "/preload",
        "/api/astraa/estimator/enforced-run",
        "/api/account/usage",
        "/api/account/estimate-credits/add",
        "/api/astraa/core/*",
    ])

    section("ACCEPTANCE TESTS BEFORE PATCH")
    print_list([
        "Allowed production origin receives expected CORS header.",
        "Unknown origin is denied or does not receive permissive CORS header.",
        "Localhost origin allowed only when ASTRAA_ALLOW_LOCALHOST_CORS=true.",
        "Auth block-mode proof still passes.",
        "Auth override-mode proof still passes.",
        "Staging pipeline proof still passes.",
        "Preload/payment route still returns JSON from allowed origin.",
    ])

    section("PATCH SEQUENCE")
    print_list([
        "Step 1: Add CORS/domain inventory script.",
        "Step 2: Add CORS acceptance-test script.",
        "Step 3: Patch CORS configuration with strict allowlist and localhost override.",
        "Step 4: Run post-auth-hardening proof.",
        "Step 5: Run payment/preload regression.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not change CORS behavior.")
    print("This script did not change deployment behavior.")


if __name__ == "__main__":
    main()
