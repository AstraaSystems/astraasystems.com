#!/usr/bin/env python3
"""
Astraa Patch: Production Identity Resolver Stub

PATCH SCRIPT.

Purpose:
- Add a disabled-by-default production identity resolver stub to api.py.
- Prepare for managed auth provider / OIDC / JWT integration.
- Keep current internal QA dev-session behavior unchanged.
- Keep broad paid SaaS onboarding blocked.

Does NOT:
- connect an auth provider
- create production sessions
- replace dev-login
- change /api/auth/me behavior
- change Estimator/payment behavior
- open customer access
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re


ROOT = Path(".")
TARGET = ROOT / "api.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"production_identity_resolver_stub_{STAMP}"

START = "# ASTRAA_PRODUCTION_IDENTITY_RESOLVER_STUB_V1_START"
END = "# ASTRAA_PRODUCTION_IDENTITY_RESOLVER_STUB_V1_END"

STUB = r'''
# ASTRAA_PRODUCTION_IDENTITY_RESOLVER_STUB_V1_START
def astraa_auth_mode():
    """
    Return the configured Astraa auth mode.

    Current safe default:
    - internal_qa_dev_session

    Future production modes:
    - production_session
    - production_jwt
    - provider_oidc
    - managed_auth

    This helper does not enable production auth by itself.
    """
    return os.getenv("ASTRAA_AUTH_MODE", "internal_qa_dev_session").strip().lower()


def astraa_production_identity_stub_enabled():
    """
    Explicit guard for the production identity resolver stub.

    This must remain false unless intentionally testing the stub.
    It does not connect a real auth provider.
    """
    return (
        os.getenv("ASTRAA_ENABLE_PRODUCTION_IDENTITY_STUB", "false")
        .strip()
        .lower()
        == "true"
    )


def astraa_resolve_production_identity(req):
    """
    Disabled-by-default production identity resolver stub.

    Future purpose:
    - Resolve managed auth / OIDC / JWT / secure session identity.
    - Map provider identity into Astraa account_id, primary_email, tenant_id, roles.
    - Preserve the rule that frontend account_email never controls authorization.

    Current behavior:
    - Always fails closed.
    - Does not trust request payload.
    - Does not create sessions.
    - Does not open paid SaaS access.
    """

    mode = astraa_auth_mode()

    allowed_future_modes = {
        "production_session",
        "production_jwt",
        "provider_oidc",
        "managed_auth",
    }

    if mode not in allowed_future_modes:
        return None, {
            "status": "blocked",
            "auth_mode": mode,
            "identity_source": "production_identity_disabled",
            "reason": (
                "Production identity resolver is disabled for the current auth mode. "
                "Current internal QA/dev-session behavior remains separate."
            ),
        }

    if not astraa_production_identity_stub_enabled():
        return None, {
            "status": "blocked",
            "auth_mode": mode,
            "identity_source": "production_identity_stub_disabled",
            "reason": (
                "Production identity resolver stub is present but disabled. "
                "Connect and prove a managed auth provider before using production identity."
            ),
        }

    return None, {
        "status": "blocked",
        "auth_mode": mode,
        "identity_source": "production_identity_provider_not_connected",
        "reason": (
            "Production identity provider adapter is not implemented yet. "
            "No production identity was resolved and no customer access was opened."
        ),
    }
# ASTRAA_PRODUCTION_IDENTITY_RESOLVER_STUB_V1_END

'''.lstrip()


def main():
    print("=" * 100)
    print("ASTRAA PRODUCTION IDENTITY RESOLVER STUB PATCH")
    print("=" * 100)
    print("Mode: PATCH api.py")
    print("Target:", TARGET)
    print("Backup directory:", BACKUP_DIR)

    if not TARGET.exists():
        raise SystemExit("Missing api.py")

    original = TARGET.read_text(encoding="utf-8", errors="ignore")

    if START in original and END in original:
        print("Production identity resolver stub already exists. No changes made.")
        return

    marker = '@app.post("/api/auth/dev-login")'
    idx = original.find(marker)

    if idx == -1:
        marker = "@app.route(\"/api/auth/dev-login\""
        idx = original.find(marker)

    if idx == -1:
        raise SystemExit("Could not locate dev-login route marker for safe insertion.")

    text = original[:idx] + STUB + original[idx:]

    backup_path = BACKUP_DIR / TARGET
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(original, encoding="utf-8")

    TARGET.write_text(text, encoding="utf-8")

    print("PATCHED:", TARGET)
    print("")
    print("Safety confirmation:")
    print("- This patch did not connect an auth provider.")
    print("- This patch did not create production sessions.")
    print("- This patch did not replace dev-login.")
    print("- This patch did not change /api/auth/me behavior.")
    print("- This patch did not change Estimator/payment behavior.")
    print("- This patch did not open customer access.")
    print("- This patch did not deploy Astraa.")


if __name__ == "__main__":
    main()
