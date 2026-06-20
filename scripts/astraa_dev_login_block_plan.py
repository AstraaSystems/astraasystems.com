#!/usr/bin/env python3
"""
Astraa Dev Login Production-Mode Block Plan

READ-ONLY SCRIPT.

Purpose:
- Plan a safe block for /api/auth/dev-login in public/production mode.
- Do not patch api.py yet.
- Define environment flags, behavior, acceptance tests, and rollback path.

Does NOT:
- modify api.py
- change auth behavior
- create users
- create sessions
- delete sessions
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
    section("ASTRAA DEV LOGIN PRODUCTION-MODE BLOCK PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("TARGET ROUTE")
    print("/api/auth/dev-login")

    section("PROPOSED RULE")
    print_list([
        "If ASTRAA_PUBLIC_LAUNCH_MODE=true and ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE is not true, block /api/auth/dev-login.",
        "Return clean JSON 403 instead of issuing a dev token.",
        "Do not remove the route yet; keep it for internal QA with explicit override.",
        "Keep /api/auth/me unchanged for now.",
        "Keep existing dev-session storage for local QA mode only.",
    ])

    section("PROPOSED BLOCK RESPONSE")
    print("""{
  "gateway": "Astraa Gateway",
  "status": "blocked",
  "reason": "Development login is disabled in public launch mode.",
  "review_note": "Set ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true only for intentional internal QA."
}""")

    section("ENVIRONMENT FLAGS")
    print_list([
        "ASTRAA_PUBLIC_LAUNCH_MODE=true means public/production-style guard mode.",
        "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true allows dev-login only for intentional internal QA.",
        "Default behavior should be safest: block dev-login when public launch mode is on.",
    ])

    section("ACCEPTANCE TESTS AFTER PATCH")
    print_list([
        "With ASTRAA_PUBLIC_LAUNCH_MODE=true and no override, /api/auth/dev-login returns 403 JSON.",
        "With ASTRAA_PUBLIC_LAUNCH_MODE=true and ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true, dev-login still issues token for internal QA.",
        "With dev-login override enabled, /api/auth/me still resolves bearer token.",
        "Estimator authenticated regression still passes with internal QA token.",
        "Payment verification replay still uses authenticated account, not payload account_email.",
        "Unauthenticated estimator behavior remains clean JSON.",
        "Staging pipeline proof still passes.",
    ])

    section("PATCH TARGET")
    print_list([
        "Locate the /api/auth/dev-login route in api.py.",
        "Add a small guard at the beginning of the route before issuing token.",
        "Do not touch payment verification logic.",
        "Do not touch Estimator enforcement logic.",
        "Do not touch Moneris preload/receipt logic.",
        "Do not touch staging DB scripts.",
    ])

    section("ROLLBACK PLAN")
    print_list([
        "Use git restore api.py if local patch fails before commit.",
        "If committed and broken, revert the specific dev-login block commit.",
        "Run auth acceptance tests before and after rollback.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not change auth behavior.")
    print("This script did not create users or sessions.")


if __name__ == "__main__":
    main()
