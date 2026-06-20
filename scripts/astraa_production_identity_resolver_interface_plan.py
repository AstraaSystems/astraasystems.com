#!/usr/bin/env python3
"""
Astraa Production Identity Resolver Interface Plan

READ-ONLY SCRIPT.

Purpose:
- Define the provider-agnostic resolver interface that future production auth should implement.
- Keep current dev-session/internal QA resolver separate and blocked by default in public launch mode.
- Define expected inputs, outputs, failure modes, route integration points, and acceptance tests.

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
import json


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def print_list(items):
    for item in items:
        print("-", item)


RESOLVER_INTERFACE = {
    "function_name": "astraa_resolve_production_identity",
    "inputs": {
        "request": "Flask request object or provider-neutral request context",
        "required_headers": [
            "Authorization, if using bearer/JWT",
            "Cookie, if using secure server session",
        ],
        "optional_context": [
            "route_name",
            "required_role",
            "required_tool",
            "tenant_hint",
        ],
    },
    "success_output": {
        "status": "ok",
        "identity": {
            "account_id": "string",
            "primary_email": "verified email string",
            "tenant_id": "string",
            "roles": ["owner/admin/member/contractor/internal_qa"],
            "selected_plan": "string or null",
            "selected_tool": "string or null",
            "subscription_status": "active/inactive/trial/canceled or null",
            "payment_status": "active/inactive/verified/blocked or null",
            "identity_source": "production_session or production_jwt",
            "auth_provider": "provider identifier",
            "provider_subject": "provider stable subject id",
        },
    },
    "failure_output": {
        "status": "blocked",
        "http_status": 401,
        "reason": "Missing, expired, invalid, or unauthorized production identity.",
    },
}


def main():
    section("ASTRAA PRODUCTION IDENTITY RESOLVER INTERFACE PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("WHY THIS INTERFACE EXISTS")
    print_list([
        "Astraa routes need one provider-agnostic way to resolve authenticated identity.",
        "The selected auth provider can change, but route authorization should not change every time.",
        "The resolver should map provider identity into Astraa account_id and tenant_id before route use.",
        "The resolver must preserve the rule that frontend account_email is never trusted for authorization.",
    ])

    section("PROPOSED RESOLVER INTERFACE")
    print(json.dumps(RESOLVER_INTERFACE, indent=2, sort_keys=True))

    section("PROPOSED FUNCTION CONTRACT")
    print("""
def astraa_resolve_production_identity(request):
    \"\"\"
    Resolve authenticated production identity from secure session/JWT/provider context.

    Returns:
        (identity, None) on success
        (None, error_response_tuple) on failure

    Must not:
        - trust browser-submitted account_email
        - create accounts implicitly
        - bypass subscription/payment state
        - expose provider secrets
    \"\"\"
""".strip())

    section("SUCCESS RULES")
    print_list([
        "A valid production session/JWT/provider token is present.",
        "Provider identity is verified by the selected provider/session mechanism.",
        "Provider subject maps to an Astraa account_id.",
        "Astraa account maps to a tenant_id.",
        "Backend account/payment/subscription state is resolved after account mapping.",
        "identity_source is set to production_session, production_jwt, or provider_oidc.",
    ])

    section("FAILURE RULES")
    print_list([
        "Missing auth should return clean JSON 401/403.",
        "Expired token/session should return clean JSON 401/403.",
        "Invalid signature/session should return clean JSON 401/403.",
        "Provider subject with no Astraa account mapping should be blocked until onboarding flow exists.",
        "Account without active payment/subscription should be blocked for paid Estimator access.",
        "Tenant mismatch should be blocked for Core OS/customer-facing workspace routes.",
    ])

    section("ROUTE INTEGRATION POINTS")
    print_list([
        "/api/auth/me should use the resolver and return the safe identity object.",
        "/api/astraa/estimator/enforced-run should use resolver identity for account lookup.",
        "/api/payment/verify-moneris-receipt should apply payment only to resolver identity account.",
        "/api/account/usage should restrict lookup to resolver identity account unless internal/admin mode.",
        "/api/account/estimate-credits/add should require payment/admin/internal authority.",
        "/api/astraa/core/* should require resolver tenant_id before customer-facing access.",
    ])

    section("DEV-SESSION SEPARATION")
    print_list([
        "Current dev-session resolver remains internal QA only.",
        "Dev-login remains blocked in public launch mode by default.",
        "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true remains an explicit internal QA override only.",
        "Production resolver should not depend on dev-session JSON files.",
        "Proof scripts should continue supporting internal QA override for regression testing.",
    ])

    section("ACCEPTANCE TESTS BEFORE IMPLEMENTATION")
    print_list([
        "Unauthenticated /api/auth/me returns clean JSON 401/403 in production-auth mode.",
        "Authenticated production identity returns account_id, primary_email, tenant_id, roles, identity_source.",
        "Invalid/expired token is rejected.",
        "Payload account_email mismatch cannot hijack account-scoped actions.",
        "Active paid account can run Estimator.",
        "Inactive/unpaid account is blocked from Estimator.",
        "Payment verification applies only to authenticated account.",
        "Core OS customer-facing routes require tenant_id.",
        "Existing post-auth-hardening proof remains passing for internal QA mode.",
        "CORS hardening proof remains passing.",
        "Gunicorn smoke test remains passing.",
    ])

    section("SAFE IMPLEMENTATION SEQUENCE")
    print_list([
        "Step 1: Add production identity resolver interface stub, disabled by default.",
        "Step 2: Add tests for missing/invalid production identity behavior.",
        "Step 3: Add provider/session adapter only after provider selection.",
        "Step 4: Map provider_subject to Astraa account_id and tenant_id.",
        "Step 5: Wire /api/auth/me to production resolver behind an explicit mode flag.",
        "Step 6: Extend Estimator/payment/account routes after /api/auth/me is proven.",
        "Step 7: Run post-auth, CORS, Gunicorn, staging, and payment proofs after every patch.",
    ])

    section("DO NOT PATCH YET")
    print_list([
        "Do not replace dev-session resolver yet.",
        "Do not remove internal QA override yet.",
        "Do not trust frontend account_email.",
        "Do not implement provider-specific code before provider selection.",
        "Do not store auth provider secrets in git.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not change auth behavior.")
    print("This script did not create users or sessions.")
    print("This script did not connect to an auth provider.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
