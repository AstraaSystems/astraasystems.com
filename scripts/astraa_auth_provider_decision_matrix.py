#!/usr/bin/env python3
"""
Astraa Production Auth Provider Decision Matrix

READ-ONLY SCRIPT.

Purpose:
- Compare production auth/session path options at planning level.
- Recommend a safe staged direction without implementing provider auth.

Does NOT:
- modify api.py
- change auth behavior
- create users
- create sessions
- connect to an auth provider
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
    section("ASTRAA PRODUCTION AUTH PROVIDER DECISION MATRIX")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("CURRENT AUTH STATE")
    print_list([
        "Dev-login is blocked in public launch mode by default.",
        "Internal QA override exists only with ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true.",
        "Backend account authority and payload account_email hijack protection are proven.",
        "Production auth provider/session is not implemented yet.",
    ])

    section("OPTION 1 — MANAGED AUTH / HOSTED LOGIN")
    print_list([
        "Good for faster production readiness.",
        "Reduces custom password/security burden.",
        "Should support verified email/session/JWT identity.",
        "Still needs mapping into Astraa account_id and tenant_id.",
        "Recommended as first serious production direction if compatible with deployment platform.",
    ])

    section("OPTION 2 — OIDC / JWT PROVIDER")
    print_list([
        "Good long-term provider-agnostic path.",
        "Works well with production_jwt auth mode.",
        "Requires signature validation, issuer/audience checks, expiry handling, and provider_subject mapping.",
        "Good if Astraa later supports business SSO.",
    ])

    section("OPTION 3 — CUSTOM EMAIL/PASSWORD")
    print_list([
        "Highest security burden.",
        "Requires password hashing, reset flow, verification, lockout/rate limits, session revocation, breach handling.",
        "Not recommended as first path unless necessary.",
    ])

    section("RECOMMENDED ASTRAA PATH")
    print_list([
        "Use provider-agnostic identity contract first.",
        "Prefer managed auth or OIDC/JWT over custom password auth.",
        "Implement provider adapter behind astraa_resolve_production_identity interface.",
        "Keep internal QA dev-session path separate and blocked by default.",
        "Do not open customer Workspace broadly until production auth is proven.",
    ])

    section("DECISION CRITERIA")
    print_list([
        "Verified email support.",
        "Session/JWT validation support.",
        "Secure secret management.",
        "Easy mapping from provider_subject to Astraa account_id.",
        "Support for future organization/tenant/team access.",
        "Good logs/audit trail.",
        "Reasonable early-stage cost.",
        "Easy rollback if provider path changes.",
    ])

    section("NEXT IMPLEMENTATION STEP AFTER DECISION")
    print_list([
        "Add production identity resolver stub disabled by default.",
        "Add missing/invalid production identity acceptance tests.",
        "Add provider adapter only after provider is selected.",
        "Wire /api/auth/me first before Estimator/payment routes.",
        "Run production auth readiness, CORS, Gunicorn, staging, and payment proofs.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not change auth behavior.")
    print("This script did not create users or sessions.")
    print("This script did not connect to an auth provider.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
