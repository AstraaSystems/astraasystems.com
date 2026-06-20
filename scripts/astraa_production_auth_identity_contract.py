#!/usr/bin/env python3
"""
Astraa Production Auth Identity Contract

READ-ONLY SCRIPT.

Purpose:
- Define the canonical authenticated identity object for future production auth.
- Keep provider-specific auth separate from Astraa's internal account/tenant contract.
- Document required fields, optional fields, validation rules, route expectations, and examples.

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


IDENTITY_CONTRACT = {
    "account_id": {
        "required": True,
        "type": "string",
        "description": "Stable Astraa account identifier. For now this may match primary_email; later it may become an internal UUID.",
    },
    "primary_email": {
        "required": True,
        "type": "string",
        "description": "Verified login email from production auth provider/session.",
    },
    "tenant_id": {
        "required": True,
        "type": "string",
        "description": "Astraa tenant/organization boundary used for Workspace/Core OS isolation.",
    },
    "roles": {
        "required": True,
        "type": "array[string]",
        "description": "Authorization roles such as owner, admin, member, contractor, internal_qa, support.",
    },
    "selected_plan": {
        "required": False,
        "type": "string",
        "description": "Resolved plan for selected tool/account. Should come from backend subscription/payment state, not frontend payload.",
    },
    "selected_tool": {
        "required": False,
        "type": "string",
        "description": "Resolved tool context, e.g. Astraa Estimator.",
    },
    "subscription_status": {
        "required": False,
        "type": "string",
        "description": "Backend subscription status, e.g. active, inactive, canceled, trial.",
    },
    "payment_status": {
        "required": False,
        "type": "string",
        "description": "Backend payment status, e.g. active, inactive, verified, blocked.",
    },
    "identity_source": {
        "required": True,
        "type": "string",
        "description": "Source of identity resolution. Future values: production_session, production_jwt, provider_oidc. Current internal QA value: dev_session_bearer_token.",
    },
    "auth_provider": {
        "required": False,
        "type": "string",
        "description": "Provider identifier after provider is selected, e.g. managed_auth, oidc, microsoft, google.",
    },
    "provider_subject": {
        "required": False,
        "type": "string",
        "description": "Provider's stable subject/user ID. Should not replace Astraa account_id directly without mapping.",
    },
    "issued_at": {
        "required": False,
        "type": "string/datetime",
        "description": "Session/token issued timestamp if available.",
    },
    "expires_at": {
        "required": False,
        "type": "string/datetime",
        "description": "Session/token expiry timestamp if available.",
    },
}


EXAMPLE_INTERNAL_QA_IDENTITY = {
    "account_id": "approved.live.test@astraasystems.com",
    "primary_email": "approved.live.test@astraasystems.com",
    "tenant_id": "tenant_approved_live_test_astraasystems_com",
    "roles": ["internal_qa"],
    "selected_plan": "Professional",
    "selected_tool": "Astraa Estimator",
    "subscription_status": "active",
    "payment_status": "active",
    "identity_source": "dev_session_bearer_token",
}


EXAMPLE_FUTURE_PRODUCTION_IDENTITY = {
    "account_id": "acct_01EXAMPLE",
    "primary_email": "customer@example.com",
    "tenant_id": "tenant_01EXAMPLE",
    "roles": ["owner"],
    "selected_plan": "Professional",
    "selected_tool": "Astraa Estimator",
    "subscription_status": "active",
    "payment_status": "active",
    "identity_source": "production_session",
    "auth_provider": "provider_name_here",
    "provider_subject": "provider_subject_here",
    "issued_at": "2026-01-01T00:00:00Z",
    "expires_at": "2026-01-01T12:00:00Z",
}


def main():
    section("ASTRAA PRODUCTION AUTH IDENTITY CONTRACT")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("WHY THIS CONTRACT EXISTS")
    print_list([
        "Production auth provider implementation should produce a consistent Astraa identity object.",
        "Astraa routes should authorize using this backend-resolved identity, not frontend account_email.",
        "Provider-specific data should be mapped into Astraa account_id and tenant_id before use.",
        "The same identity contract should power /api/auth/me, Estimator access, payment verification, account usage, and Core OS tenant isolation.",
    ])

    section("CANONICAL IDENTITY FIELDS")
    for field, spec in IDENTITY_CONTRACT.items():
        print(f"\n{field}")
        print(f"  required: {spec['required']}")
        print(f"  type: {spec['type']}")
        print(f"  description: {spec['description']}")

    section("NON-NEGOTIABLE VALIDATION RULES")
    print_list([
        "account_id must be present for authenticated account-scoped actions.",
        "primary_email must be verified by the auth/session provider.",
        "tenant_id must be present before opening customer-facing Core OS routes.",
        "identity_source must clearly identify how identity was resolved.",
        "Browser-submitted account_email must never override authenticated identity.",
        "selected_plan, payment_status, and subscription_status must come from backend account/payment state.",
        "provider_subject must be mapped to an Astraa account before account-scoped access is granted.",
    ])

    section("ROUTE EXPECTATIONS")
    print_list([
        "/api/auth/me should return this identity contract, minus sensitive provider/session internals.",
        "/api/astraa/estimator/enforced-run should use account_id/primary_email from identity, not payload account_email.",
        "/api/payment/verify-moneris-receipt should apply payment to authenticated account identity only.",
        "/api/account/usage should restrict results to authenticated account unless internal/admin mode.",
        "/api/account/estimate-credits/add should require payment/admin/internal authority.",
        "/api/astraa/core/* should require tenant_id before customer-facing access.",
    ])

    section("CURRENT INTERNAL QA IDENTITY EXAMPLE")
    print(json.dumps(EXAMPLE_INTERNAL_QA_IDENTITY, indent=2, sort_keys=True))

    section("FUTURE PRODUCTION IDENTITY EXAMPLE")
    print(json.dumps(EXAMPLE_FUTURE_PRODUCTION_IDENTITY, indent=2, sort_keys=True))

    section("PROVIDER-AGNOSTIC DESIGN RULE")
    print("Production auth provider can change, but Astraa route authorization should keep using this contract.")

    section("NEXT SAFE STEP")
    print("Create production identity resolver interface plan — still no auth behavior patch.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not change auth behavior.")
    print("This script did not create users or sessions.")
    print("This script did not connect to an auth provider.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
