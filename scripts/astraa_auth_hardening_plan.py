#!/usr/bin/env python3
"""
Astraa Auth Hardening Plan

READ-ONLY SCRIPT.

Purpose:
- Print a phased production-auth hardening plan before any auth patching.
- Preserve current working payment/Estimator/staging proof paths.
- Define auth milestones, route targets, session model, guard rules, and acceptance tests.

Does NOT:
- modify api.py
- change auth behavior
- create users
- create sessions
- delete sessions
- migrate data
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
    section("ASTRAA AUTH HARDENING PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Purpose: Plan production auth hardening before touching auth code.")

    section("CURRENT KNOWN AUTH SURFACE")
    print_list([
        "/api/auth/dev-login currently exists as a development bridge.",
        "/api/auth/me should remain as an identity inspection endpoint but later resolve production identity.",
        "Bearer-token identity currently supports local development/session testing.",
        "Account authority guard must remain for payment verification and Estimator actions.",
        "Browser-submitted account_email must never override authenticated identity.",
        "Request guard and public launch mode should remain part of the production safety model.",
    ])

    section("NON-NEGOTIABLE AUTH PRINCIPLES")
    print_list([
        "Authenticated identity is the source of truth.",
        "Browser-submitted account_email is never trusted for account-scoped actions.",
        "Payment verification must apply only to the authenticated account.",
        "Estimator access must be based on authenticated account status and backend usage record.",
        "Dev-login must not be publicly usable in production launch mode.",
        "Production auth changes must not break the proven Moneris/payment/usage/staging proof chain.",
    ])

    section("PHASE 0 — PRESERVE WORKING INTERNAL QA MODE")
    print_list([
        "Keep /api/auth/dev-login for local/internal QA only while production auth is planned.",
        "Keep /api/auth/me available for identity inspection.",
        "Keep current backend token identity working for internal regression tests.",
        "Keep ASTRAA_PUBLIC_LAUNCH_MODE and ASTRAA_REQUEST_GUARD_ENABLED enabled during hardening tests.",
        "Do not remove dev-login until a production auth replacement is implemented and tested.",
    ])

    section("PHASE 1 — DEFINE PRODUCTION IDENTITY CONTRACT")
    print_list([
        "Canonical identity fields: account_id, primary_email, tenant_id, selected_plan, roles, identity_source.",
        "Identity source should become production_session or production_jwt after provider integration.",
        "Account lookup should resolve subscription/payment state from backend storage, not frontend payload.",
        "Missing/expired/invalid session should return clean JSON 401/403 responses.",
        "Tenant isolation must be explicit before Core OS customer-facing routes are opened.",
    ])

    section("PHASE 2 — SELECT PRODUCTION AUTH PROVIDER")
    print_list([
        "Choose a provider path before patching: managed auth service, OAuth/OIDC provider, or Microsoft/Google business login.",
        "Keep login/register public UX stable while backend provider is selected.",
        "Avoid exposing internal implementation names on public pages.",
        "Plan secure session cookie or verified JWT flow depending on provider.",
        "Plan password reset/email verification only if provider requires custom handling.",
    ])

    section("PHASE 3 — ROUTE HARDENING TARGETS")
    print_list([
        "/api/auth/dev-login: block in production/public launch mode unless explicit internal override is set.",
        "/api/auth/me: resolve identity from production session/JWT, not dev token.",
        "/api/payment/verify-moneris-receipt: require authenticated account authority.",
        "/api/astraa/estimator/enforced-run: require authenticated identity and ignore payload account_email.",
        "/api/account/usage: restrict account-scoped lookup to authenticated account unless internal/admin mode.",
        "/api/account/estimate-credits/add: require verified payment/admin/internal authority before adding credits.",
        "Core OS routes: require tenant/account identity before customer-facing usage.",
    ])

    section("PHASE 4 — SESSION / TOKEN STORAGE TARGET")
    print_list([
        "Move production sessions away from local dev-session JSON.",
        "Use secure cookie/session or verified JWT depending on chosen provider.",
        "Define session expiry, rotation, revocation, and logout behavior.",
        "Keep local JSON dev sessions only for internal QA mode.",
        "Do not store payment proof in browser sessionStorage.",
    ])

    section("PHASE 5 — SECURITY GUARDS TO PRESERVE")
    print_list([
        "Account authority guard remains required.",
        "Payload account_email hijack protection remains required.",
        "Payment idempotency remains required.",
        "Request guard and rate limiting remain required.",
        "Production simulation guard for Moneris remains required.",
        "Schema validation remains required for payment and Estimator requests.",
    ])

    section("PHASE 6 — ACCEPTANCE TESTS BEFORE AUTH PATCH")
    print_list([
        "Unauthenticated Estimator run is blocked.",
        "Authenticated active paid account can run Estimator.",
        "Authenticated inactive/unpaid account is blocked.",
        "Payload account_email different from authenticated account cannot hijack access.",
        "Payment verification applies once only for same ticket/account/purchase type.",
        "Dev-login is blocked in production/public launch mode unless internal override is explicitly enabled.",
        "CORS allows only approved Astraa domains before public launch.",
        "Core OS customer-facing routes are blocked without tenant/account identity.",
    ])

    section("PHASE 7 — SAFE PATCH SEQUENCE")
    print_list([
        "Step 1: Add auth acceptance-test script first.",
        "Step 2: Add dev-login production-mode block with explicit internal override.",
        "Step 3: Preserve local/internal QA path for regression tests.",
        "Step 4: Add production identity resolver interface, initially inactive.",
        "Step 5: Wire provider-specific auth only after provider is chosen.",
        "Step 6: Run payment/Estimator/staging pipeline proofs after every auth change.",
    ])

    section("DO NOT PATCH YET")
    print("This plan does not change auth behavior.")
    print("Next safe step is a read-only auth acceptance-test script.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not create users.")
    print("This script did not create sessions.")
    print("This script did not delete sessions.")
    print("This script did not change auth behavior.")


if __name__ == "__main__":
    main()
