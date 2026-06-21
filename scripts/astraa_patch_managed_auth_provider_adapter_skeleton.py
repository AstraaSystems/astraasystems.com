#!/usr/bin/env python3
"""
Astraa Patch: Managed Auth Provider Adapter Skeleton

PATCH SCRIPT.

Purpose:
- Add a disabled/fail-closed managed auth provider adapter skeleton to api.py.
- Prepare for Supabase Auth, Clerk, Auth0, Microsoft/Entra OIDC, or another OIDC/JWT provider.
- Keep provider-neutral behavior until actual provider selection and credentials are configured.

Does NOT:
- connect an auth provider
- validate real JWTs
- create users
- create sessions
- replace dev-login
- change /api/auth/me behavior
- change Estimator/payment behavior
- open customer access
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime


ROOT = Path(".")
TARGET = ROOT / "api.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"managed_auth_provider_adapter_skeleton_{STAMP}"

START = "# ASTRAA_MANAGED_AUTH_PROVIDER_ADAPTER_SKELETON_V1_START"
END = "# ASTRAA_MANAGED_AUTH_PROVIDER_ADAPTER_SKELETON_V1_END"

INSERT_AFTER = "# ASTRAA_PRODUCTION_IDENTITY_RESOLVER_STUB_V1_END"

SKELETON = r'''

# ASTRAA_MANAGED_AUTH_PROVIDER_ADAPTER_SKELETON_V1_START
def astraa_managed_auth_provider():
    """
    Return the configured managed auth provider name.

    Expected future values:
    - supabase
    - clerk
    - auth0
    - microsoft_entra
    - custom_oidc

    This helper does not connect to the provider.
    """
    return os.getenv("ASTRAA_MANAGED_AUTH_PROVIDER", "").strip().lower()


def astraa_managed_auth_required_env():
    """
    Provider-neutral required environment variable names.

    These are placeholders for future provider integration.
    Presence checks must never print secret values.
    """
    return [
        "ASTRAA_AUTH_MODE",
        "ASTRAA_MANAGED_AUTH_PROVIDER",
        "ASTRAA_AUTH_ISSUER",
        "ASTRAA_AUTH_AUDIENCE",
        "ASTRAA_AUTH_JWKS_URL",
        "ASTRAA_AUTH_CLIENT_ID",
    ]


def astraa_managed_auth_config_status():
    """
    Return provider configuration status without exposing secret values.

    This is a safe presence check only.
    It does not validate tokens, connect to JWKS, or create sessions.
    """
    required = astraa_managed_auth_required_env()
    missing = [
        name for name in required
        if not os.getenv(name, "").strip()
    ]

    provider = astraa_managed_auth_provider()

    return {
        "configured": not missing and bool(provider),
        "provider": provider or None,
        "missing": missing,
        "secret_values_exposed": False,
    }


def astraa_resolve_managed_auth_identity(req):
    """
    Fail-closed managed auth provider adapter skeleton.

    Future purpose:
    - Validate provider session/JWT/OIDC identity.
    - Map provider subject to Astraa account_id.
    - Map verified email to primary_email.
    - Map organization/account context to tenant_id.
    - Return the canonical Astraa identity contract.

    Current behavior:
    - Always returns blocked.
    - Does not trust request payload.
    - Does not create sessions.
    - Does not open customer access.
    """
    status = astraa_managed_auth_config_status()

    if not status.get("configured"):
        return None, {
            "status": "blocked",
            "identity_source": "managed_auth_provider_not_configured",
            "provider": status.get("provider"),
            "missing": status.get("missing"),
            "reason": (
                "Managed auth provider adapter skeleton is present but provider configuration "
                "is incomplete. No production identity was resolved."
            ),
        }

    return None, {
        "status": "blocked",
        "identity_source": "managed_auth_provider_adapter_not_implemented",
        "provider": status.get("provider"),
        "reason": (
            "Managed auth provider configuration is present, but token/session validation "
            "is not implemented yet. No customer access was opened."
        ),
    }
# ASTRAA_MANAGED_AUTH_PROVIDER_ADAPTER_SKELETON_V1_END

'''.lstrip()


def main():
    print("=" * 100)
    print("ASTRAA MANAGED AUTH PROVIDER ADAPTER SKELETON PATCH")
    print("=" * 100)
    print("Mode: PATCH api.py")
    print("Target:", TARGET)
    print("Backup directory:", BACKUP_DIR)

    if not TARGET.exists():
        raise SystemExit("Missing api.py")

    original = TARGET.read_text(encoding="utf-8", errors="ignore")

    if START in original and END in original:
        print("Managed auth provider adapter skeleton already exists. No changes made.")
        return

    idx = original.find(INSERT_AFTER)
    if idx == -1:
        raise SystemExit("Could not locate production identity resolver stub end marker.")

    insert_at = idx + len(INSERT_AFTER)
    text = original[:insert_at] + "\n" + SKELETON + original[insert_at:]

    backup_path = BACKUP_DIR / TARGET
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(original, encoding="utf-8")

    TARGET.write_text(text, encoding="utf-8")

    print("PATCHED:", TARGET)
    print("")
    print("Safety confirmation:")
    print("- This patch did not connect an auth provider.")
    print("- This patch did not validate real JWTs.")
    print("- This patch did not create users.")
    print("- This patch did not create sessions.")
    print("- This patch did not replace dev-login.")
    print("- This patch did not change /api/auth/me behavior.")
    print("- This patch did not change Estimator/payment behavior.")
    print("- This patch did not open customer access.")
    print("- This patch did not deploy Astraa.")


if __name__ == "__main__":
    main()
