"""
ASTRAA BACKEND ENFORCEMENT NOTE

The current frontend portal uses browser sessionStorage for estimate usage during
internal testing and live soft-launch validation.

Production estimate limits must be enforced by the backend.

Required production rules:

Trial:
- 15 total estimates
- 1 estimate per day
- 15-day trial window
- backend account identity required

Basic:
- 30 estimates per monthly billing period
- active payment/subscription required

Professional:
- 120 estimates per monthly billing period
- active payment/subscription required

Custom / Franchise / Enterprise:
- usage limits should be read from custom package configuration or agreement

Important:
- Browser sessionStorage must not be trusted for production enforcement.
- payment-success.html is a customer-facing/session confirmation only.
- Official payment proof must be confirmed through Moneris merchant/admin records.
- Backend should eventually store account, subscription, payment status, estimate usage,
  trial dates, billing period dates, and custom package limits.

See BACKEND_ENFORCEMENT_NOTES.md for the full enforcement plan.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
import os
import json
import uuid
import requests
import hashlib

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv(override=True)

from lead_capture import astraa_leads
app = Flask(__name__)
app.register_blueprint(astraa_leads)



@app.route("/health", methods=["GET"])
def astraa_health():
    return {
        "status": "ok",
        "service": "astraa-api",
    }, 200


# ASTRAA_CORS_DOMAIN_LOCK_V1
def astraa_cors_public_launch_mode():
    return os.getenv("ASTRAA_PUBLIC_LAUNCH_MODE", "false").strip().lower() == "true"


def astraa_cors_allowed_origins():
    configured = os.getenv(
        "ASTRAA_ALLOWED_ORIGINS",
        "https://astraasystems.com,https://www.astraasystems.com"
    )

    origins = {
        item.strip().rstrip("/")
        for item in configured.split(",")
        if item.strip()
    }

    allow_localhost = os.getenv("ASTRAA_ALLOW_LOCALHOST_CORS", "false").strip().lower() == "true"

    if allow_localhost:
        origins.update({
            "http://localhost:5000",
            "http://localhost:8000",
            "http://127.0.0.1:5000",
            "http://127.0.0.1:8000",
        })

    return origins


def astraa_cors_remove_permissive_headers(response):
    for header_name in [
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Methods",
    ]:
        try:
            response.headers.pop(header_name, None)
        except Exception:
            pass

    response.headers["Vary"] = "Origin"
    return response


@app.after_request
def astraa_apply_cors_domain_lock(response):
    if not astraa_cors_public_launch_mode():
        return response

    origin = request.headers.get("Origin")

    if not origin:
        return astraa_cors_remove_permissive_headers(response)

    normalized_origin = origin.strip().rstrip("/")
    allowed_origins = astraa_cors_allowed_origins()

    if normalized_origin not in allowed_origins:
        return astraa_cors_remove_permissive_headers(response)

    response.headers["Access-Control-Allow-Origin"] = normalized_origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Vary"] = "Origin"

    return response


CORS(app)

# -------------------------------------------------
# Astraa API security
# -------------------------------------------------
API_KEY = os.getenv("ASTRAA_API_KEY", "astraa_secure")

# -------------------------------------------------
# Moneris production credentials
# -------------------------------------------------
MONERIS_STORE_ID = os.getenv("MONERIS_STORE_ID", "")
MONERIS_API_TOKEN = os.getenv("MONERIS_API_TOKEN", "")
MONERIS_CHECKOUT_ID = os.getenv("MONERIS_CHECKOUT_ID", "")
MONERIS_ENV = os.getenv("MONERIS_ENV", "prod").lower()

# -------------------------------------------------
# Optional safe testing override
# If you want to charge a small production test amount,
# set ASTRAA_TEST_AMOUNT=2.00 in .env
# If empty, real plan prices are used.
# -------------------------------------------------
ASTRAA_TEST_AMOUNT = os.getenv("ASTRAA_TEST_AMOUNT", "").strip()

# -------------------------------------------------
# Files
# -------------------------------------------------
PAYMENTS_FILE = "payments.jsonl"
PRELOADS_FILE = "preloads.jsonl"
RECEIPTS_FILE = "receipts.jsonl"

# -------------------------------------------------
# Plan pricing
# -------------------------------------------------
PLAN_PRICES = {
    "basic": "39.00",
    "professional": "99.00"
}

PLAN_LABELS = {
    "basic": "Astraa Basic",
    "professional": "Astraa Professional"
}

# -------------------------------------------------
# Moneris endpoints
# -------------------------------------------------
if MONERIS_ENV == "prod":
    MONERIS_REQUEST_URL = "https://gateway.moneris.com/chkt/request/request.php"
    MONERIS_ENV_VALUE = "prod"
else:
    MONERIS_REQUEST_URL = "https://gatewayt.moneris.com/chkt/request/request.php"
    MONERIS_ENV_VALUE = "qa"

# ASTRAA_MONERIS_CREDENTIAL_GUARD_V1
_MONERIS_PLACEHOLDERS = {
    "", "LOCAL_DISABLED", "REPLACE_WITH_SECURE_SECRET",
    "MONERIS_STORE_ID", "MONERIS_API_TOKEN", "MONERIS_CHECKOUT_ID",
    "PASTE_STORE_ID", "PASTE_CHECKOUT_ID", "PASTE_CURRENT_API_TOKEN",
}
if MONERIS_ENV_VALUE == "prod":
    _astraa_bad_creds = [
        _name for _name, _val in (
            ("MONERIS_STORE_ID", MONERIS_STORE_ID),
            ("MONERIS_API_TOKEN", MONERIS_API_TOKEN),
            ("MONERIS_CHECKOUT_ID", MONERIS_CHECKOUT_ID),
        )
        if (_val or "").strip() in _MONERIS_PLACEHOLDERS
    ]
    if _astraa_bad_creds:
        print("=" * 64)
        print("!!! ASTRAA PROD CHECKOUT BLOCKED - placeholder/empty credentials !!!")
        print("Offending vars:", ", ".join(_astraa_bad_creds))
        print("Set real Moneris values in .env before taking payments.")
        print("=" * 64)
        raise RuntimeError(
            "Astraa refusing to start in prod with placeholder Moneris credentials: "
            + ", ".join(_astraa_bad_creds)
        )
# END ASTRAA_MONERIS_CREDENTIAL_GUARD_V1


# -------------------------------------------------
# Utility helpers
# -------------------------------------------------
def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_jsonl(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def authorized(req):
    return req.headers.get("X-API-KEY") == API_KEY


def safe_amount(value):
    """
    Validate and normalize amount to Moneris-style decimal string.
    Example: 39.00
    """
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
        if amount <= 0:
            return None
        return f"{amount:.2f}"
    except (InvalidOperation, ValueError):
        return None


def get_plan_amount(plan):
    """
    Server-side plan pricing.
    The frontend may send amount, but backend controls final amount.
    """
    normalized_plan = (plan or "professional").lower().strip()

    if normalized_plan not in PLAN_PRICES:
        normalized_plan = "professional"

    if ASTRAA_TEST_AMOUNT:
        test_amount = safe_amount(ASTRAA_TEST_AMOUNT)
        if test_amount:
            return normalized_plan, test_amount

    return normalized_plan, PLAN_PRICES[normalized_plan]


def get_plan_label(plan):
    return PLAN_LABELS.get(plan, "Astraa Professional")


def config_status():
    return {
        "store_id_loaded": bool(MONERIS_STORE_ID),
        "api_token_loaded": bool(MONERIS_API_TOKEN),
        "checkout_id_loaded": bool(MONERIS_CHECKOUT_ID),
        "moneris_env": MONERIS_ENV_VALUE,
        "moneris_url": MONERIS_REQUEST_URL,
        "test_amount_override": ASTRAA_TEST_AMOUNT if ASTRAA_TEST_AMOUNT else None
    }

# ============================================================
# ASTRAA ESTIMATOR USAGE ENFORCEMENT — LOCAL/STAGING V1
# ============================================================

ASTRAA_USAGE_DB_PATH = os.path.join("astraa_data", "astraa_usage_db.json")

ESTIMATOR_PLAN_LIMITS = {
    "Trial": {
        "estimate_limit": 15,
        "daily_limit": 1,
        "requires_payment": False,
        "period_type": "trial_15_days"
    },
    "Basic": {
        "estimate_limit": 30,
        "daily_limit": None,
        "requires_payment": True,
        "period_type": "monthly"
    },
    "Professional": {
        "estimate_limit": 120,
        "daily_limit": None,
        "requires_payment": True,
        "period_type": "monthly"
    }
}


def astraa_today_date():
    return datetime.now(timezone.utc).date()


def astraa_today_key():
    return astraa_today_date().isoformat()


def astraa_month_key():
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m")


def astraa_month_start():
    now = datetime.now(timezone.utc)
    return now.replace(day=1).date().isoformat()


def astraa_month_end():
    now = datetime.now(timezone.utc)
    if now.month == 12:
        next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month + 1, day=1)

    return (next_month.date() - timedelta(days=1)).isoformat()


def astraa_load_usage_db():
    os.makedirs("astraa_data", exist_ok=True)

    if not os.path.exists(ASTRAA_USAGE_DB_PATH):
        return {}

    try:
        with open(ASTRAA_USAGE_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}

    except Exception:
        return {}


def astraa_save_usage_db(db):
    os.makedirs("astraa_data", exist_ok=True)

    tmp_path = ASTRAA_USAGE_DB_PATH + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, sort_keys=True)

    os.replace(tmp_path, ASTRAA_USAGE_DB_PATH)


def astraa_default_usage_record(account_email, plan):
    plan_rules = ESTIMATOR_PLAN_LIMITS.get(plan, ESTIMATOR_PLAN_LIMITS["Trial"])

    return {
        "account_id": account_email,
        "primary_email": account_email,
        "business_name": "",
        "selected_tool": "Astraa Estimator",
        "selected_plan": plan,
        "payment_status": "trial" if plan == "Trial" else "inactive",
        "subscription_status": "trial" if plan == "Trial" else "inactive",

        "billing_period_key": astraa_month_key(),
        "billing_period_start": astraa_month_start(),
        "billing_period_end": astraa_month_end(),

        "estimate_limit": plan_rules["estimate_limit"],
        "estimate_used": 0,

        "trial_start_date": astraa_today_key() if plan == "Trial" else None,
        "last_trial_estimate_date": None,
        "daily_limit": plan_rules["daily_limit"],

        "extra_estimate_credits_total": 0,
        "extra_estimate_credits_used": 0,

        "custom_limit_config": None,
        "saved_estimates": [],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


def astraa_get_usage_record(account_email, requested_plan="Trial"):
    # ASTRAA_USAGE_STORAGE_WRAPPER_ADOPTION_V1
    db = astraa_storage_load_usage_db()

    account_email = str(account_email or "").strip().lower()
    if not account_email:
        account_email = "anonymous@astraa.local"

    if account_email not in db:
        db[account_email] = astraa_default_usage_record(account_email, requested_plan)
        astraa_storage_save_usage_db(db)

    return db, db[account_email]


def astraa_reset_monthly_period_if_needed(record):
    current_key = astraa_month_key()

    if record.get("billing_period_key") != current_key:
        record["billing_period_key"] = current_key
        record["billing_period_start"] = astraa_month_start()
        record["billing_period_end"] = astraa_month_end()
        record["estimate_used"] = 0
        record["extra_estimate_credits_used"] = 0
        record["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return record


def astraa_trial_expired(record):
    trial_start = record.get("trial_start_date")

    if not trial_start:
        return False

    try:
        start_date = date.fromisoformat(trial_start)
        days_used = (astraa_today_date() - start_date).days
        return days_used >= 15
    except Exception:
        return False


def astraa_effective_estimate_allowance(record):
    base_limit = int(record.get("estimate_limit") or 0)
    extra_total = int(record.get("extra_estimate_credits_total") or 0)
    extra_used = int(record.get("extra_estimate_credits_used") or 0)
    extra_remaining = max(extra_total - extra_used, 0)

    return base_limit + extra_remaining


def astraa_enforce_estimator_usage(record):
    plan = record.get("selected_plan") or "Trial"
    tool = record.get("selected_tool") or "Astraa Estimator"

    if tool != "Astraa Estimator":
        return False, "Selected tool is not Astraa Estimator.", record

    if plan in ["Basic", "Professional"]:
        record = astraa_reset_monthly_period_if_needed(record)

    if plan == "Trial":
        if astraa_trial_expired(record):
            return False, "Trial period expired.", record

        if int(record.get("estimate_used") or 0) >= 15:
            return False, "Trial estimate limit reached.", record

        if record.get("last_trial_estimate_date") == astraa_today_key():
            return False, "Daily trial estimate limit reached.", record

        return True, "Allowed", record

    if plan in ["Basic", "Professional"]:
        if record.get("payment_status") != "active" or record.get("subscription_status") != "active":
            return False, "Payment/subscription is not active.", record

        allowance = astraa_effective_estimate_allowance(record)
        used = int(record.get("estimate_used") or 0)

        if used >= allowance:
            return False, "Monthly estimate limit reached. Add an estimate pack or upgrade.", record

        return True, "Allowed", record

    if plan in ["Custom", "Franchise", "Enterprise"]:
        if record.get("payment_status") != "active" or record.get("subscription_status") != "active":
            return False, "Custom package payment/subscription is not active.", record

        custom_config = record.get("custom_limit_config") or {}
        custom_limit = int(custom_config.get("estimate_limit") or record.get("estimate_limit") or 0)

        if custom_limit and int(record.get("estimate_used") or 0) >= custom_limit:
            return False, "Custom package estimate limit reached.", record

        return True, "Allowed", record

    return False, "Unsupported Estimator plan.", record


def astraa_record_successful_estimator_usage(db, record, estimate_summary):
    plan = record.get("selected_plan") or "Trial"

    record["estimate_used"] = int(record.get("estimate_used") or 0) + 1

    if plan == "Trial":
        record["last_trial_estimate_date"] = astraa_today_key()

    base_limit = int(record.get("estimate_limit") or 0)

    # If user has exceeded base plan limit because of extra packs,
    # count the overflow against extra_estimate_credits_used.
    if record["estimate_used"] > base_limit:
        overflow = record["estimate_used"] - base_limit
        record["extra_estimate_credits_used"] = min(
            overflow,
            int(record.get("extra_estimate_credits_total") or 0)
        )

    record.setdefault("saved_estimates", [])
    record["saved_estimates"].append({
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "backend_estimator_usage_enforcement",
        "estimate": estimate_summary
    })

    record["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    db[record["account_id"]] = record
    astraa_storage_save_usage_db(db)

    return record

# -------------------------------------------------
# Startup debug
# -------------------------------------------------
print("======================================")
print("Astraa API starting")
print("MONERIS_STORE_ID loaded:", bool(MONERIS_STORE_ID))
print("MONERIS_API_TOKEN loaded:", bool(MONERIS_API_TOKEN))
print("MONERIS_CHECKOUT_ID loaded:", bool(MONERIS_CHECKOUT_ID))
print("MONERIS_ENV:", MONERIS_ENV_VALUE)
print("MONERIS URL:", MONERIS_REQUEST_URL)
print("ASTRAA_TEST_AMOUNT:", ASTRAA_TEST_AMOUNT if ASTRAA_TEST_AMOUNT else "not set")
print("======================================")


# -------------------------------------------------
# Health
# -------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Astraa API running",
        "config": config_status()
    })


# -------------------------------------------------

# ASTRAA_PRELOAD_PUBLIC_CHECKOUT_AUTH_V1
def astraa_allow_public_checkout_preload(req):
    """
    Allows the public Astraa payment page to request a Moneris Checkout preload ticket.

    This does not activate user access.
    This does not verify payment.
    This does not expose Moneris credentials.
    It only creates a checkout ticket using server-side credentials.
    """
    try:
        data = req.get_json(silent=True) or {}

        email = (
            data.get("email")
            or data.get("checkout_email")
            or data.get("account_email")
            or ""
        ).strip().lower()

        selected_tool = (
            data.get("selected_tool")
            or data.get("tool")
            or ""
        ).strip().lower()

        selected_plan = (
            data.get("selected_plan")
            or data.get("plan")
            or ""
        ).strip().lower()

        allowed_tool = (
            selected_tool in ["astraa estimator", "estimator", ""]
            or "estimator" in selected_tool
        )

        allowed_plan = selected_plan in [
            "trial",
            "basic",
            "professional",
            "estimate_pack",
            "estimate_pack_10",
            ""
        ]

        valid_email = "@" in email and "." in email

        return bool(allowed_tool and allowed_plan and valid_email)

    except Exception:
        return False





# ASTRAA_DEV_SESSION_AUTH_V1
ASTRAA_SESSIONS_DB_PATH = os.path.join("astraa_data", "astraa_sessions.json")


def astraa_load_sessions_db():
    os.makedirs("astraa_data", exist_ok=True)

    if not os.path.exists(ASTRAA_SESSIONS_DB_PATH):
        return {}

    try:
        with open(ASTRAA_SESSIONS_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def astraa_save_sessions_db(db):
    os.makedirs("astraa_data", exist_ok=True)

    tmp_path = ASTRAA_SESSIONS_DB_PATH + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, sort_keys=True)

    os.replace(tmp_path, ASTRAA_SESSIONS_DB_PATH)


def astraa_extract_bearer_token(req):
    try:
        auth_header = req.headers.get("Authorization", "")
    except Exception:
        return ""

    if not auth_header:
        return ""

    parts = auth_header.strip().split(" ", 1)

    if len(parts) != 2:
        return ""

    scheme, token = parts

    if scheme.lower() != "bearer":
        return ""

    return token.strip()


def astraa_session_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def astraa_create_dev_session(account_email, selected_plan="Professional"):
    account_email = astraa_clean_email(account_email)

    if not account_email:
        return None

    token = "astraa_dev_" + uuid.uuid4().hex + uuid.uuid4().hex

    # ASTRAA_SESSION_STORAGE_WRAPPER_ADOPTION_V1
    db = astraa_storage_load_sessions_db()

    db[token] = {
        "account_email": account_email,
        "account_id": account_email,
        "tenant_id": "tenant_" + account_email.replace("@", "_").replace(".", "_"),
        "selected_plan": selected_plan or "Professional",
        "identity_source": "dev_session",
        "created_at": astraa_session_now(),
        "updated_at": astraa_session_now()
    }

    astraa_storage_save_sessions_db(db)

    return token


def astraa_resolve_session_identity(req):
    token = astraa_extract_bearer_token(req)

    if not token:
        return None

    db = astraa_storage_load_sessions_db()
    session = db.get(token)

    if not session:
        return None

    account_email = astraa_clean_email(session.get("account_email"))

    if not account_email:
        return None

    return {
        "allowed": True,
        "account_email": account_email,
        "account_id": session.get("account_id") or account_email,
        "tenant_id": session.get("tenant_id"),
        "selected_plan": session.get("selected_plan"),
        "identity_source": "dev_session_bearer_token",
        "reason": "Backend session token resolved account identity."
    }


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



@app.post("/api/auth/dev-login")
def astraa_dev_login():
    # ASTRAA_DEV_LOGIN_PUBLIC_MODE_BLOCK_V1
    public_launch_mode = os.getenv("ASTRAA_PUBLIC_LAUNCH_MODE", "false").strip().lower() == "true"
    allow_dev_login_public_mode = os.getenv("ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE", "false").strip().lower() == "true"

    if public_launch_mode and not allow_dev_login_public_mode:
        return jsonify({
            "gateway": "Astraa Gateway",
            "status": "blocked",
            "reason": "Development login is disabled in public launch mode.",
            "review_note": "Set ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true only for intentional internal QA."
        }), 403

    """
    Development/staging account session endpoint.
    This is a bridge toward proper backend-authenticated identity.
    Do not treat this as final public authentication.
    """
    payload = request.get_json(silent=True) or {}

    account_email = astraa_clean_email(
        payload.get("account_email")
        or payload.get("email")
        or payload.get("checkout_email")
    )

    selected_plan = payload.get("selected_plan") or payload.get("plan") or "Professional"

    if not account_email or "@" not in account_email:
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "reason": "Valid account_email is required for dev login."
        }), 400

    token = astraa_create_dev_session(account_email, selected_plan)

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "token": token,
        "account_email": account_email,
        "selected_plan": selected_plan,
        "identity_source": "dev_session",
        "review_note": "Development session issued. Replace with production auth/session before public launch."
    }), 200


@app.get("/api/auth/me")
def astraa_auth_me():
    identity = astraa_resolve_session_identity(request)

    if not identity:
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "reason": "No valid backend session token found."
        }), 401

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "identity": {
            "account_email": identity.get("account_email"),
            "account_id": identity.get("account_id"),
            "tenant_id": identity.get("tenant_id"),
            "selected_plan": identity.get("selected_plan"),
            "identity_source": identity.get("identity_source")
        }
    }), 200






# ASTRAA_ESTIMATOR_SCHEMA_VALIDATION_V1
def astraa_parse_float_field(value, field_name, minimum=None, maximum=None, required=True):
    if value is None or value == "":
        if required:
            return None, f"{field_name} is required."
        return None, None

    try:
        parsed = float(value)
    except Exception:
        return None, f"{field_name} must be numeric."

    if minimum is not None and parsed < minimum:
        return None, f"{field_name} must be at least {minimum}."

    if maximum is not None and parsed > maximum:
        return None, f"{field_name} must be at most {maximum}."

    return parsed, None


def astraa_validate_estimator_inputs(inputs):
    if not isinstance(inputs, dict):
        return False, ["inputs must be an object."], {}

    errors = []
    clean = {}

    allowed_plans = {"trial", "basic", "professional", "custom", ""}
    selected_plan = str(inputs.get("selected_plan") or "").strip().lower()

    if selected_plan not in allowed_plans:
        errors.append("selected_plan must be Trial, Basic, Professional, or Custom.")

    clean["selected_plan"] = selected_plan

    field_specs = {
        "base_cost": (0, 100000000),
        "complexity_factor": (0.1, 10),
        "material_multiplier": (0.1, 10),
        "labor_multiplier": (0.1, 10),
        "location_multiplier": (0.1, 10),
    }

    for field, (minimum, maximum) in field_specs.items():
        required = field in ["base_cost", "complexity_factor"]
        parsed, error = astraa_parse_float_field(
            inputs.get(field),
            field,
            minimum=minimum,
            maximum=maximum,
            required=required
        )

        if error:
            errors.append(error)
        elif parsed is not None:
            clean[field] = parsed

    clean.setdefault("material_multiplier", 1.0)
    clean.setdefault("labor_multiplier", 1.0)
    clean.setdefault("location_multiplier", 1.0)

    return len(errors) == 0, errors, clean


# ASTRAA_REQUEST_GUARD_V1
ASTRAA_RATE_LIMIT_BUCKETS = {}


def astraa_request_guard_enabled():
    return (
        os.getenv("ASTRAA_REQUEST_GUARD_ENABLED", "true")
        .strip()
        .lower()
        in ["1", "true", "yes"]
    )


def astraa_max_request_bytes():
    try:
        return int(os.getenv("ASTRAA_MAX_REQUEST_BYTES", "262144"))
    except Exception:
        return 262144


def astraa_client_ip(req):
    forwarded = req.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return req.remote_addr or "unknown"


def astraa_route_rate_limit(path):
    """
    Returns (limit, window_seconds).
    These are conservative local defaults and can be tuned by env later.
    """
    if path == "/preload":
        return 20, 60

    if path == "/api/payment/verify-moneris-receipt":
        return 30, 60

    if path == "/api/astraa/estimator/enforced-run":
        return 60, 60

    if path == "/api/auth/dev-login":
        return 20, 60

    return 120, 60


def astraa_rate_limit_check(req):
    import time

    path = req.path or "/"
    ip = astraa_client_ip(req)
    limit, window = astraa_route_rate_limit(path)

    now = time.time()
    key = f"{ip}:{path}"

    entries = ASTRAA_RATE_LIMIT_BUCKETS.get(key, [])
    entries = [ts for ts in entries if now - ts < window]

    if len(entries) >= limit:
        ASTRAA_RATE_LIMIT_BUCKETS[key] = entries
        return False, {
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "reason": "Rate limit exceeded.",
            "route": path,
            "retry_after_seconds": window,
            "review_note": "Request blocked by Astraa request guard."
        }

    entries.append(now)
    ASTRAA_RATE_LIMIT_BUCKETS[key] = entries
    return True, None


@app.before_request
def astraa_request_guard():
    if not astraa_request_guard_enabled():
        return None

    if request.method == "OPTIONS":
        return None

    max_bytes = astraa_max_request_bytes()
    content_length = request.content_length

    if content_length is not None and content_length > max_bytes:
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "reason": "Request body too large.",
            "max_request_bytes": max_bytes,
            "review_note": "Request blocked by Astraa request size guard."
        }), 413

    ok, payload = astraa_rate_limit_check(request)

    if not ok:
        return jsonify(payload), 429

    return None




# ASTRAA_PRELOAD_SCHEMA_VALIDATION_V1
def astraa_validate_preload_payload(payload):
    """
    Validate public checkout preload input before creating a Moneris ticket.
    Billing amount is still controlled server-side by get_plan_amount / ASTRAA_TEST_AMOUNT.
    """
    if not isinstance(payload, dict):
        return False, ["payload must be an object."], {}

    errors = []
    clean = dict(payload)

    email = (
        payload.get("email")
        or payload.get("checkout_email")
        or payload.get("account_email")
        or ""
    )
    email = str(email or "").strip().lower()

    if not email or "@" not in email or "." not in email:
        errors.append("email must be valid.")

    clean["email"] = email
    clean["checkout_email"] = email

    selected_tool = str(
        payload.get("selected_tool")
        or payload.get("tool")
        or "Astraa Estimator"
    ).strip()

    selected_tool_l = selected_tool.lower()

    allowed_tools = {
        "astraa estimator",
        "estimator",
        ""
    }

    if selected_tool_l not in allowed_tools:
        errors.append("selected_tool must be Astraa Estimator for this checkout flow.")

    clean["selected_tool"] = "Astraa Estimator"
    clean["tool"] = "Astraa Estimator"

    selected_plan = str(
        payload.get("selected_plan")
        or payload.get("plan")
        or "professional"
    ).strip().lower()

    allowed_plans = {
        "trial",
        "basic",
        "professional",
        "custom",
        "estimate_pack",
        "estimate_pack_10",
        "extra_estimate_pack",
        "extra_estimate_pack_10"
    }

    if selected_plan not in allowed_plans:
        errors.append("selected_plan/plan must be a known Astraa checkout plan.")

    clean["plan"] = selected_plan
    clean["selected_plan"] = selected_plan.title() if selected_plan in ["trial", "basic", "professional", "custom"] else selected_plan

    amount = payload.get("amount")

    if amount not in [None, ""]:
        try:
            amount_value = float(amount)
            if amount_value <= 0:
                errors.append("amount must be greater than 0 when provided.")
            if amount_value > 100000:
                errors.append("amount is too large.")
        except Exception:
            errors.append("amount must be numeric when provided.")

    return len(errors) == 0, errors, clean


# Moneris Checkout Preload
# -------------------------------------------------
@app.route("/preload", methods=["POST"])
def preload():
    # ASTRAA_PRELOAD_SCHEMA_VALIDATION_ROUTE_GUARD_V1
    preload_payload = request.get_json(silent=True) or {}
    valid_preload_payload, preload_payload_errors, clean_preload_payload = astraa_validate_preload_payload(preload_payload)

    if not valid_preload_payload:
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "reason": "Invalid preload input.",
            "errors": preload_payload_errors,
            "review_note": "Preload request blocked by schema validation before Moneris."
        }), 400

    # Use sanitized preload data downstream.
    preload_payload = clean_preload_payload

    if not authorized(request) and not astraa_allow_public_checkout_preload(request):
        return jsonify({
            "status": "error",
            "message": "unauthorized",
            "moneris_error": {},
            "review_note": "Astraa preload request was blocked before Moneris. Request was not authorized and did not match the public checkout preload shape."
        }), 403

    if not MONERIS_STORE_ID or not MONERIS_API_TOKEN or not MONERIS_CHECKOUT_ID:
        return jsonify({
            "response": {
                "success": "false",
                "error": {
                    "config": {
                        "data": "Missing MONERIS_STORE_ID, MONERIS_API_TOKEN, or MONERIS_CHECKOUT_ID"
                    }
                }
            }
        }), 500

    data = preload_payload

    email = (data.get("email") or "").strip()
    requested_plan = (data.get("plan") or "professional").strip().lower()

    plan, amount = get_plan_amount(requested_plan)
    plan_label = get_plan_label(plan)

    order_no = "ASTRAA-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6].upper()

    # ASTRAA_PRELOAD_KNOWN_GOOD_PAYLOAD_V1
    # This payload shape matches the direct Moneris diagnostic that successfully returned a ticket.
    payload = {
        "store_id": MONERIS_STORE_ID,
        "api_token": MONERIS_API_TOKEN,
        "checkout_id": MONERIS_CHECKOUT_ID,
        "txn_total": amount,
        "environment": MONERIS_ENV_VALUE,
        "action": "preload",
        "order_no": order_no,
        "language": "en",
        "cust_info": {
            "email": email if email else "customer@astraasystems.com"
        },
        "cart": {
            "items": [
                {
                    "description": plan_label,
                    "product_code": plan,
                    "unit_cost": amount,
                    "quantity": "1"
                }
            ],
            "subtotal": amount
        }
    }

    preload_record = {
        "timestamp": now_iso(),
        "order_no": order_no,
        "email": email,
        "plan": plan,
        "amount": amount,
        "moneris_env": MONERIS_ENV_VALUE,
        "status": "initiated"
    }

    # ASTRAA_EVENT_LOG_STORAGE_ADOPTION_V1
    astraa_storage_append_event_log("preloads", preload_record)

    try:
        response = requests.post(
            MONERIS_REQUEST_URL,
            json=payload,
            timeout=30
        )

        raw_text = response.text

        print("MONERIS PRELOAD HTTP STATUS:", response.status_code)
        print("MONERIS PRELOAD RAW:", raw_text)

        try:
            moneris_data = response.json()
        except Exception:
            error_payload = {
                "response": {
                    "success": "false",
                    "error": {
                        "gateway": {
                            "data": "Moneris returned non-JSON response",
                            "http_status": response.status_code,
                            "raw": raw_text
                        }
                    }
                }
            }

            preload_record["status"] = "failed_non_json"
            preload_record["raw_response"] = raw_text
            astraa_storage_append_event_log("preloads", preload_record)

            return jsonify(error_payload), 500

        preload_record["status"] = "response_received"
        preload_record["moneris_response"] = moneris_data
        astraa_storage_append_event_log("preloads", preload_record)

        # Log payment session if ticket received
        if (
            isinstance(moneris_data, dict)
            and moneris_data.get("response", {}).get("success") == "true"
            and moneris_data.get("response", {}).get("ticket")
        ):
            payment_record = {
                "timestamp": now_iso(),
                "order_no": order_no,
                "email": email,
                "plan": plan,
                "amount": amount,
                "ticket": moneris_data["response"]["ticket"],
                "status": "ticket_created"
            }
            astraa_storage_append_event_log("payments", payment_record)

        # ASTRAA_PRELOAD_RESPONSE_COMPAT_V1
        # Return both the original Moneris response and top-level compatibility fields
        # so payment.html can reliably start checkout.
        try:
            response_obj = moneris_data.get("response", {}) if isinstance(moneris_data, dict) else {}
            ticket = response_obj.get("ticket")
            success = response_obj.get("success")
            moneris_error = response_obj.get("error", {})

            if str(success).lower() == "true" and ticket:
                return jsonify({
                    "status": "ok",
                    "success": True,
                    "ticket": ticket,
                    "order_no": order_no,
                    "environment": MONERIS_ENV_VALUE,
                    "response": response_obj
                })

            return jsonify({
                "status": "error",
                "success": False,
                "message": (
                    moneris_error.get("message")
                    if isinstance(moneris_error, dict)
                    else "Payment preload failed."
                ) or "Payment preload failed.",
                "moneris_error": moneris_error,
                "response": response_obj,
                "review_note": "Moneris preload did not return a usable checkout ticket."
            }), 403

        except Exception:
            return jsonify(moneris_data)

    except requests.exceptions.RequestException as e:
        error_payload = {
            "response": {
                "success": "false",
                "error": {
                    "exception": {
                        "data": str(e)
                    }
                }
            }
        }

        preload_record["status"] = "request_exception"
        preload_record["error"] = str(e)
        astraa_storage_append_event_log("preloads", preload_record)

        return jsonify(error_payload), 500


# -------------------------------------------------
# Moneris Checkout Receipt Request
# Used after payment_complete callback later.
# -------------------------------------------------
@app.route("/receipt", methods=["POST"])
def receipt():
    if not authorized(request):
        return jsonify({
            "status": "error",
            "message": "unauthorized"
        }), 403

    data = request.json or {}
    ticket = (data.get("ticket") or "").strip()

    if not ticket:
        return jsonify({
            "response": {
                "success": "false",
                "error": {
                    "ticket": {
                        "data": "Missing ticket"
                    }
                }
            }
        }), 400

    if not MONERIS_STORE_ID or not MONERIS_API_TOKEN or not MONERIS_CHECKOUT_ID:
        return jsonify({
            "response": {
                "success": "false",
                "error": {
                    "config": {
                        "data": "Missing MONERIS_STORE_ID, MONERIS_API_TOKEN, or MONERIS_CHECKOUT_ID"
                    }
                }
            }
        }), 500

    payload = {
        "store_id": MONERIS_STORE_ID,
        "api_token": MONERIS_API_TOKEN,
        "checkout_id": MONERIS_CHECKOUT_ID,
        "ticket": ticket,
        "environment": MONERIS_ENV_VALUE,
        "action": "receipt"
    }

    receipt_record = {
        "timestamp": now_iso(),
        "ticket": ticket,
        "status": "initiated"
    }

    astraa_storage_append_event_log("receipts", receipt_record)

    try:
        response = requests.post(
            MONERIS_REQUEST_URL,
            json=payload,
            timeout=30
        )

        raw_text = response.text

        print("MONERIS RECEIPT HTTP STATUS:", response.status_code)
        print("MONERIS RECEIPT RAW:", raw_text)

        try:
            moneris_data = response.json()
        except Exception:
            receipt_record["status"] = "failed_non_json"
            receipt_record["raw_response"] = raw_text
            astraa_storage_append_event_log("receipts", receipt_record)

            return jsonify({
                "response": {
                    "success": "false",
                    "error": {
                        "gateway": {
                            "data": "Moneris returned non-JSON response",
                            "http_status": response.status_code,
                            "raw": raw_text
                        }
                    }
                }
            }), 500

        receipt_record["status"] = "response_received"
        receipt_record["moneris_response"] = moneris_data
        astraa_storage_append_event_log("receipts", receipt_record)

        return jsonify(moneris_data)

    except requests.exceptions.RequestException as e:
        receipt_record["status"] = "request_exception"
        receipt_record["error"] = str(e)
        astraa_storage_append_event_log("receipts", receipt_record)

        return jsonify({
            "response": {
                "success": "false",
                "error": {
                    "exception": {
                        "data": str(e)
                    }
                }
            }
        }), 500


# -------------------------------------------------
# Optional simple lead endpoint for later use
# -------------------------------------------------
@app.route("/lead", methods=["POST"])
def lead():
    if not authorized(request):
        return jsonify({
            "status": "error",
            "message": "unauthorized"
        }), 403

    data = request.json or {}

    record = {
        "timestamp": now_iso(),
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "company": data.get("company", ""),
        "request_type": data.get("request_type", ""),
        "message": data.get("message", "")
    }

    astraa_storage_append_event_log("leads", record)

    return jsonify({
        "status": "ok",
        "message": "Lead captured"
    })


# -------------------------------------------------
# Run server
# -------------------------------------------------

# -------------------------------------------------------------------
# ASTRAA ESTIMATE USAGE API
# Backend-side estimate usage tracking and soft-launch enforcement.
#
# Current purpose:
# - Move estimate usage rules out of browser-only sessionStorage.
# - Track Trial / Basic / Professional estimate usage on backend.
# - Provide API endpoints the portal can call later.
#
# Production note:
# - This local JSON store is for soft launch/testing.
# - Replace with a real database before larger public launch.
# - Official paid access should eventually be verified by Moneris records.
# -------------------------------------------------------------------

import json
import os
from pathlib import Path
from datetime import datetime, date, timedelta, timezone

ASTRAA_DATA_DIR = Path(os.getenv("ASTRAA_DATA_DIR", "astraa_data"))
ASTRAA_DATA_DIR.mkdir(parents=True, exist_ok=True)

ASTRAA_USAGE_DB_PATH = Path(
    os.getenv("ASTRAA_USAGE_DB_PATH", str(ASTRAA_DATA_DIR / "astraa_usage_db.json"))
)

# Soft-launch switch:
# false = allow Basic/Professional usage even if payment_status is not active yet.
# true  = require payment_status == active for paid plans.
ASTRAA_REQUIRE_ACTIVE_PAYMENT = os.getenv(
    "ASTRAA_REQUIRE_ACTIVE_PAYMENT",
    "false"
).lower() == "true"

# Dev-only reset switch:
# true allows POST /api/account/usage/reset
ASTRAA_ALLOW_USAGE_RESET = os.getenv(
    "ASTRAA_ALLOW_USAGE_RESET",
    "true"
).lower() == "true"


def astraa_today_key():
    return date.today().isoformat()


def astraa_month_key():
    today = date.today()
    return f"{today.year:04d}-{today.month:02d}"


def astraa_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def astraa_normalize_email(value):
    return str(value or "").strip().lower()


def astraa_json_response(payload, status=200):
    try:
        return jsonify(payload), status
    except NameError:
        # If jsonify was not imported in older api.py, import it lazily.
        from flask import jsonify as _jsonify
        return _jsonify(payload), status


def astraa_get_request_json():
    try:
        return request.get_json(silent=True) or {}
    except NameError:
        from flask import request as _request
        return _request.get_json(silent=True) or {}


def astraa_get_query_arg(name, default=""):
    try:
        return request.args.get(name, default)
    except NameError:
        from flask import request as _request
        return _request.args.get(name, default)


def astraa_load_usage_db():
    if not ASTRAA_USAGE_DB_PATH.exists():
        return {}

    try:
        with ASTRAA_USAGE_DB_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

        return {}
    except Exception:
        return {}


def astraa_save_usage_db(db):
    ASTRAA_USAGE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    tmp = ASTRAA_USAGE_DB_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, sort_keys=True)

    tmp.replace(ASTRAA_USAGE_DB_PATH)


def astraa_plan_config(plan):
    plan = str(plan or "Trial").strip()

    if plan == "Trial":
        return {
            "plan": "Trial",
            "estimate_limit": 15,
            "daily_limit": None,
            "period_type": "trial",
            "period_label": "15-day trial",
            "payment_required": False
        }

    if plan == "Basic":
        return {
            "plan": "Basic",
            "estimate_limit": 30,
            "daily_limit": None,
            "period_type": "monthly",
            "period_label": "Monthly",
            "payment_required": True
        }

    if plan == "Professional":
        return {
            "plan": "Professional",
            "estimate_limit": 120,
            "daily_limit": None,
            "period_type": "monthly",
            "period_label": "Monthly",
            "payment_required": True
        }

    if plan in ["Custom", "Franchise", "Enterprise"]:
        return {
            "plan": plan,
            "estimate_limit": None,
            "daily_limit": None,
            "period_type": "custom",
            "period_label": "Scoped",
            "payment_required": True
        }

    return {
        "plan": plan,
        "estimate_limit": 15,
        "daily_limit": 1,
        "period_type": "trial",
        "period_label": "15-day trial",
        "payment_required": False
    }


def astraa_default_period(config):
    today = date.today()

    if config["period_type"] == "trial":
        start = today
        end = today + timedelta(days=15)
        return start.isoformat(), end.isoformat()

    if config["period_type"] == "monthly":
        start = today.replace(day=1)

        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1)
        else:
            next_month = start.replace(month=start.month + 1)

        end = next_month - timedelta(days=1)
        return start.isoformat(), end.isoformat()

    return None, None


def astraa_account_key(email):
    email = astraa_normalize_email(email)
    if not email:
        return ""
    return email


def astraa_create_or_update_account_usage(
    email,
    selected_tool="Astraa Estimator",
    selected_plan="Trial",
    selected_price="$0 / 15 days",
    payment_status=None,
    business_name="",
    industry=""
):
    email = astraa_normalize_email(email)

    if not email:
        return None, "Missing email"

    db = astraa_storage_load_usage_db()
    key = astraa_account_key(email)
    config = astraa_plan_config(selected_plan)
    period_start, period_end = astraa_default_period(config)

    existing = db.get(key, {})

    # If plan changes, reset usage for that selected plan.
    plan_changed = existing.get("selected_plan") and existing.get("selected_plan") != selected_plan

    if payment_status is None:
        payment_status = existing.get("payment_status")

    if not payment_status:
        payment_status = "active" if selected_plan == "Trial" else "pending"

    if not existing or plan_changed:
        record = {
            "account_id": key,
            "primary_email": email,
            "business_name": business_name or existing.get("business_name", ""),
            "industry": industry or existing.get("industry", ""),
            "selected_tool": selected_tool,
            "selected_plan": selected_plan,
            "selected_price": selected_price,
            "payment_status": payment_status,
            "subscription_status": "active" if payment_status == "active" else "pending",
            "trial_start_date": astraa_today_key() if selected_plan == "Trial" else existing.get("trial_start_date"),
            "billing_period_key": astraa_month_key(),
            "billing_period_start": period_start,
            "billing_period_end": period_end,
            "estimate_limit": config["estimate_limit"],
            "estimate_used": 0,
            "last_trial_estimate_date": None,
            "period_type": config["period_type"],
            "period_label": config["period_label"],
            "daily_limit": config["daily_limit"],
            "saved_estimates": [],
            "created_at": existing.get("created_at", astraa_now_iso()),
            "updated_at": astraa_now_iso()
        }
    else:
        record = existing
        record["selected_tool"] = selected_tool or record.get("selected_tool", "Astraa Estimator")
        record["selected_plan"] = selected_plan or record.get("selected_plan", "Trial")
        record["selected_price"] = selected_price or record.get("selected_price", "$0 / 15 days")
        record["business_name"] = business_name or record.get("business_name", "")
        record["industry"] = industry or record.get("industry", "")
        record["payment_status"] = payment_status
        record["subscription_status"] = "active" if payment_status == "active" else record.get("subscription_status", "pending")
        record["estimate_limit"] = config["estimate_limit"]
        record["period_type"] = config["period_type"]
        record["period_label"] = config["period_label"]
        record["daily_limit"] = config["daily_limit"]
        record["updated_at"] = astraa_now_iso()

        # Reset monthly usage when month changes for paid monthly plans.
        if config["period_type"] == "monthly":
            current_month = astraa_month_key()
            if record.get("billing_period_key") != current_month:
                record["billing_period_key"] = current_month
                record["billing_period_start"], record["billing_period_end"] = astraa_default_period(config)
                record["estimate_used"] = 0
                record["saved_estimates"] = []

    db[key] = record
    astraa_storage_save_usage_db(db)

    return record, None


def astraa_get_usage_record(email):
    email = astraa_normalize_email(email)

    if not email:
        return None

    db = astraa_storage_load_usage_db()
    return db.get(astraa_account_key(email))


def astraa_estimate_remaining(record):
    limit = record.get("estimate_limit")

    if limit is None:
        return None

    return max(int(limit) - int(record.get("estimate_used", 0)), 0)


def astraa_usage_summary(record):
    if not record:
        return None

    return {
        "selected_tool": record.get("selected_tool"),
        "selected_plan": record.get("selected_plan"),
        "selected_price": record.get("selected_price"),
        "payment_status": record.get("payment_status"),
        "subscription_status": record.get("subscription_status"),
        "estimate_limit": record.get("estimate_limit"),
        "estimate_used": record.get("estimate_used", 0),
        "estimate_remaining": astraa_estimate_remaining(record),
        "extra_estimate_credits_total": record.get("extra_estimate_credits_total", 0),
        "estimate_credit_packs": record.get("estimate_credit_packs", []),
        "period_type": record.get("period_type"),
        "period_label": record.get("period_label"),
        "billing_period_start": record.get("billing_period_start"),
        "billing_period_end": record.get("billing_period_end"),
        "daily_limit": record.get("daily_limit"),
        "last_trial_estimate_date": record.get("last_trial_estimate_date")
    }


def astraa_enforce_estimate_limit(record):
    if not record:
        return False, "Account usage record not found."

    plan = record.get("selected_plan", "Trial")
    config = astraa_plan_config(plan)

    payment_required = config.get("payment_required", False)

    if payment_required and ASTRAA_REQUIRE_ACTIVE_PAYMENT:
        if record.get("payment_status") != "active":
            return False, "Payment is not active for this plan."

    if plan == "Trial":
        if int(record.get("estimate_used", 0)) >= 15:
            return False, "Trial estimate limit reached."

        return True, "Allowed"

    if plan == "Basic":
        if int(record.get("estimate_used", 0)) >= 30:
            return False, "Basic monthly estimate limit reached."

        return True, "Allowed"

    if plan == "Professional":
        if int(record.get("estimate_used", 0)) >= 120:
            return False, "Professional monthly estimate limit reached."

        return True, "Allowed"

    if plan in ["Custom", "Franchise", "Enterprise"]:
        # For now, custom usage is allowed unless a custom limit is later configured.
        return True, "Allowed"

    return False, "Unknown plan."



def astraa_bc_location_multiplier(location_market="BC / Vancouver"):
    """
    Stage 1 Astraa planning multipliers for BC cities and towns.

    These are relative planning factors for soft launch only.
    They are not official municipal construction cost indexes.
    Replace/expand with verified BCPI/cost-guide data over time.
    """
    key = str(location_market or "BC / Vancouver").strip()

    multipliers = {
        "BC / Vancouver": 1.00,
        "BC / Burnaby": 0.98,
        "BC / Richmond": 0.98,
        "BC / Surrey": 0.95,
        "BC / Coquitlam": 0.97,
        "BC / Port Coquitlam": 0.95,
        "BC / Port Moody": 0.98,
        "BC / New Westminster": 0.97,
        "BC / North Vancouver": 1.02,
        "BC / West Vancouver": 1.05,
        "BC / Delta": 0.96,
        "BC / Langley": 0.94,
        "BC / Maple Ridge": 0.93,
        "BC / Pitt Meadows": 0.94,
        "BC / White Rock": 0.99,

        "BC / Abbotsford": 0.91,
        "BC / Chilliwack": 0.89,
        "BC / Mission": 0.90,
        "BC / Hope": 0.88,

        "BC / Victoria": 0.96,
        "BC / Saanich": 0.96,
        "BC / Langford": 0.93,
        "BC / Colwood": 0.93,
        "BC / Nanaimo": 0.90,
        "BC / Parksville": 0.90,
        "BC / Qualicum Beach": 0.91,
        "BC / Duncan": 0.88,
        "BC / Courtenay": 0.88,
        "BC / Comox": 0.89,
        "BC / Campbell River": 0.87,
        "BC / Port Alberni": 0.86,
        "BC / Tofino": 0.98,
        "BC / Ucluelet": 0.97,
        "BC / Powell River": 0.86,

        "BC / Squamish": 0.98,
        "BC / Whistler": 1.08,
        "BC / Pemberton": 0.98,
        "BC / Gibsons": 0.91,
        "BC / Sechelt": 0.91,

        "BC / Kelowna": 0.92,
        "BC / West Kelowna": 0.91,
        "BC / Vernon": 0.89,
        "BC / Penticton": 0.90,
        "BC / Kamloops": 0.88,
        "BC / Merritt": 0.85,
        "BC / Salmon Arm": 0.87,
        "BC / Revelstoke": 0.89,

        "BC / Cranbrook": 0.86,
        "BC / Kimberley": 0.86,
        "BC / Fernie": 0.90,
        "BC / Nelson": 0.89,
        "BC / Castlegar": 0.86,
        "BC / Trail": 0.85,
        "BC / Golden": 0.88,

        "BC / Prince George": 0.85,
        "BC / Quesnel": 0.84,
        "BC / Williams Lake": 0.84,
        "BC / Fort St. John": 0.89,
        "BC / Dawson Creek": 0.87,
        "BC / Terrace": 0.87,
        "BC / Prince Rupert": 0.90,
        "BC / Kitimat": 0.89,
        "BC / Smithers": 0.86,
        "BC / Fort Nelson": 0.88,

        "BC / Other City or Town": 0.90,
        "Canada / General": 0.92,
        "Custom Market": 1.00
    }

    return multipliers.get(key, 0.90)



def astraa_estimator_project_base_rate(project_type="Commercial"):
    """
    Base rate anchor by project type before location/calibration multiplier.
    This keeps approved calibration math independent from city default multipliers.
    """
    project_type = str(project_type or "Commercial").strip().lower()

    if "residential" in project_type:
        return 300.0

    if "commercial" in project_type:
        return 375.0

    if "renovation" in project_type:
        return 250.0

    if "service" in project_type or "repair" in project_type:
        return 190.0

    if "industrial" in project_type:
        return 325.0

    if "custom" in project_type:
        return 400.0

    return 375.0


def astraa_public_calibrated_base_rate(project_type="", location_market="BC / Vancouver", quality_level=""):
    """
    Stage 1 public-data calibration.

    Base rates are planning anchors by project type.
    Location multipliers adjust them for BC city/town selection.
    This is a soft-launch calibration layer, not a final bid source.
    """
    project_type = str(project_type or "").strip().lower()

    rates = {
        "residential": 300,
        "commercial": 375,
        "renovation": 250,
        "service / repair": 190,
        "service": 190,
        "industrial": 325,
        "custom": 400
    }

    if "residential" in project_type:
        base = rates["residential"]
    elif "commercial" in project_type:
        base = rates["commercial"]
    elif "renovation" in project_type:
        base = rates["renovation"]
    elif "service" in project_type or "repair" in project_type:
        base = rates["service / repair"]
    elif "industrial" in project_type:
        base = rates["industrial"]
    elif "custom" in project_type:
        base = rates["custom"]
    else:
        base = rates["commercial"]

    try:
        quality_level = ""
        effective_multiplier = astraa_get_effective_location_multiplier(
            location_market,
            project_type,
            quality_level
        )
    except Exception:
        effective_multiplier = astraa_bc_location_multiplier(location_market)

    return round(base * effective_multiplier, 2)


def astraa_calculate_estimate(payload):
    sqft = float(payload.get("sqft") or 0)
    material = float(payload.get("material") or 1)
    labor = float(payload.get("labor") or 1)
    complexity = float(payload.get("complexity") or 1)

    project_type = payload.get("project_type") or payload.get("projectType") or "Commercial"
    location_market = payload.get("location_market") or payload.get("location") or "BC / Vancouver"
    quality_level = payload.get("quality_level") or payload.get("qualityLevel") or "Standard"

    approved_calibration = astraa_find_approved_calibration(
        location_market,
        project_type,
        quality_level
    )

    if approved_calibration:
        effective_location_multiplier = float(approved_calibration.get("approved_multiplier"))
        base_rate = round(
            astraa_estimator_project_base_rate(project_type) * effective_location_multiplier,
            2
        )
        approved_calibration_applied = True
        approved_calibration_id = approved_calibration.get("calibration_id")
        calibration_basis = "Approved calibration override"
    else:
        base_rate = float(
            payload.get("base_rate") or
            astraa_public_calibrated_base_rate(project_type, location_market, quality_level)
        )
        approved_calibration_applied = False
        approved_calibration_id = None
        effective_location_multiplier = astraa_bc_location_multiplier(location_market)
        calibration_basis = "Stage 1 public-data calibrated baseline"

    bcpi_factor = float(payload.get("bcpi_factor") or 1.0)

    estimate = sqft * base_rate * bcpi_factor * material * labor * complexity

    return {
        "sqft": sqft,
        "material": material,
        "labor": labor,
        "complexity": complexity,
        "base_rate": base_rate,
        "bcpi_factor": bcpi_factor,
        "project_type": project_type,
        "location_market": location_market,
        "quality_level": quality_level,
        "effective_location_multiplier": effective_location_multiplier,
        "approved_calibration_applied": approved_calibration_applied,
        "approved_calibration_id": approved_calibration_id,
        "calibration_basis": calibration_basis,
        "estimate": round(estimate, 2)
    }


@app.route("/api/account/usage", methods=["GET"])
# ASTRAA_ACCOUNT_USAGE_STORAGE_WRAPPER_ADOPTION_V1
def astraa_get_account_usage():
    email = astraa_normalize_email(astraa_get_query_arg("email"))

    if not email:
        return astraa_json_response({
            "success": False,
            "error": "Missing email query parameter."
        }, 400)

    # ASTRAA_ACCOUNT_USAGE_GET_TUPLE_FIX_V1
    usage_lookup = astraa_get_usage_record(email)

    if isinstance(usage_lookup, tuple):
        _, record = usage_lookup
    else:
        record = usage_lookup

    if not record:
        return astraa_json_response({
            "success": False,
            "error": "Usage record not found.",
            "usage": None
        }, 404)

    return astraa_json_response({
        "success": True,
        "usage": astraa_usage_summary(record)
    })


@app.route("/api/account/usage", methods=["POST"])
def astraa_create_account_usage():
    payload = astraa_get_request_json()

    email = astraa_normalize_email(payload.get("email"))
    # ASTRAA_PAYMENT_SCHEMA_VALIDATION_ROUTE_GUARD_V1
    valid_payment_payload, payment_payload_errors, clean_payment_payload = astraa_validate_payment_verification_payload(payload)

    if not valid_payment_payload:
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "payment_verified": False,
            "reason": "Invalid payment verification input.",
            "errors": payment_payload_errors,
            "review_note": "Payment verification blocked by schema validation."
        }), 400

    payload.update(clean_payment_payload)

    selected_tool = payload.get("selected_tool") or "Astraa Estimator"
    selected_plan = payload.get("selected_plan") or "Trial"
    selected_price = payload.get("selected_price") or "$0 / 15 days"
    payment_status = payload.get("payment_status")
    business_name = payload.get("business_name") or ""
    industry = payload.get("industry") or ""

    record, error = astraa_create_or_update_account_usage(
        email=email,
        selected_tool=selected_tool,
        selected_plan=selected_plan,
        selected_price=selected_price,
        payment_status=payment_status,
        business_name=business_name,
        industry=industry
    )

    if error:
        return astraa_json_response({
            "success": False,
            "error": error
        }, 400)

    return astraa_json_response({
        "success": True,
        "usage": astraa_usage_summary(record)
    })


@app.route("/api/account/payment-status", methods=["POST"])
def astraa_update_payment_status():
    payload = astraa_get_request_json()

    email = astraa_normalize_email(payload.get("email"))
    payment_status = payload.get("payment_status") or "active"
    selected_tool = payload.get("selected_tool") or "Astraa Estimator"
    selected_plan = payload.get("selected_plan") or "Professional"
    selected_price = payload.get("selected_price") or "$99 CAD/month"

    record, error = astraa_create_or_update_account_usage(
        email=email,
        selected_tool=selected_tool,
        selected_plan=selected_plan,
        selected_price=selected_price,
        payment_status=payment_status,
        business_name=payload.get("business_name") or "",
        industry=payload.get("industry") or ""
    )

    if error:
        return astraa_json_response({
            "success": False,
            "error": error
        }, 400)

    return astraa_json_response({
        "success": True,
        "message": "Payment status updated.",
        "usage": astraa_usage_summary(record)
    })


@app.route("/api/estimate", methods=["POST"])
def astraa_create_estimate():
    payload = astraa_get_request_json()

    email = astraa_normalize_email(payload.get("email"))

    if not email:
        return astraa_json_response({
            "success": False,
            "error": "Missing email."
        }, 400)

    selected_tool = payload.get("selected_tool") or "Astraa Estimator"
    selected_plan = payload.get("selected_plan") or "Trial"
    selected_price = payload.get("selected_price") or "$0 / 15 days"
    payment_status = payload.get("payment_status")

    record = astraa_get_usage_record(email)

    if not record:
        record, error = astraa_create_or_update_account_usage(
            email=email,
            selected_tool=selected_tool,
            selected_plan=selected_plan,
            selected_price=selected_price,
            payment_status=payment_status,
            business_name=payload.get("business_name") or "",
            industry=payload.get("industry") or ""
        )

        if error:
            return astraa_json_response({
                "success": False,
                "error": error
            }, 400)

    allowed, reason = astraa_enforce_estimate_limit(record)

    if not allowed:
        return astraa_json_response({
            "success": False,
            "error": reason,
            "usage": astraa_usage_summary(record)
        }, 403)

    estimate_result = astraa_calculate_estimate(payload)

    db = astraa_storage_load_usage_db()
    key = astraa_account_key(email)
    record = db.get(key, record)

    record["estimate_used"] = int(record.get("estimate_used", 0)) + 1

    record["last_estimate_date"] = astraa_today_key()

    saved_estimates = record.get("saved_estimates")

    if not isinstance(saved_estimates, list):
        saved_estimates = []

    saved_estimates.append({
        "created_at": astraa_now_iso(),
        "estimate": estimate_result,
        "source": "backend_api"
    })

    record["saved_estimates"] = saved_estimates
    record["updated_at"] = astraa_now_iso()

    db[key] = record
    astraa_storage_save_usage_db(db)

    return astraa_json_response({
        "success": True,
        "estimate": estimate_result,
        "usage": astraa_usage_summary(record)
    })


@app.route("/api/account/usage/reset", methods=["POST"])
def astraa_reset_account_usage():
    if not ASTRAA_ALLOW_USAGE_RESET:
        return astraa_json_response({
            "success": False,
            "error": "Usage reset is disabled."
        }, 403)

    payload = astraa_get_request_json()
    email = astraa_normalize_email(payload.get("email"))

    if not email:
        return astraa_json_response({
            "success": False,
            "error": "Missing email."
        }, 400)

    record = astraa_get_usage_record(email)

    if not record:
        return astraa_json_response({
            "success": False,
            "error": "Usage record not found."
        }, 404)

    config = astraa_plan_config(record.get("selected_plan", "Trial"))

    record["estimate_used"] = 0
    record["last_trial_estimate_date"] = None
    record["saved_estimates"] = []
    record["estimate_limit"] = config["estimate_limit"]
    record["daily_limit"] = config["daily_limit"]
    record["period_type"] = config["period_type"]
    record["period_label"] = config["period_label"]
    record["updated_at"] = astraa_now_iso()

    db = astraa_storage_load_usage_db()
    db[astraa_account_key(email)] = record
    astraa_storage_save_usage_db(db)

    return astraa_json_response({
        "success": True,
        "message": "Usage reset.",
        "usage": astraa_usage_summary(record)
    })

# -------------------------------------------------------------------
# END ASTRAA ESTIMATE USAGE API
# -------------------------------------------------------------------



# -------------------------------------------------------------------
# ASTRAA FEEDBACK API
# Stores estimator feedback for future calibration and learning.
#
# Purpose:
# - Capture optional actual final cost
# - Capture optional written customer feedback
# - Store estimate snapshot and context
# - Calculate estimate error when actual final cost is provided
# - Support future calibration suggestions
#
# Soft-launch storage:
# - astraa_data/astraa_feedback_db.json
#
# Production note:
# - Replace JSON file with a real database later.
# - Do not auto-update pricing/calibration from feedback without review.
# -------------------------------------------------------------------

import uuid

ASTRAA_FEEDBACK_DB_PATH = Path(
    os.getenv("ASTRAA_FEEDBACK_DB_PATH", str(ASTRAA_DATA_DIR / "astraa_feedback_db.json"))
)


def astraa_load_feedback_db():
    if not ASTRAA_FEEDBACK_DB_PATH.exists():
        return []

    try:
        with ASTRAA_FEEDBACK_DB_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []
    except Exception:
        return []


def astraa_save_feedback_db(records):
    ASTRAA_FEEDBACK_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    tmp = ASTRAA_FEEDBACK_DB_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, sort_keys=True)

    tmp.replace(ASTRAA_FEEDBACK_DB_PATH)


def astraa_float_or_none(value):
    try:
        if value is None or value == "":
            return None

        return float(value)
    except Exception:
        return None


def astraa_extract_estimate_amount(payload):
    """
    Attempts to extract the best available estimate amount from the feedback payload.

    Priority:
    1. total_budget_estimate
    2. hard_cost_estimate
    3. latest_estimate.estimate.estimate
    4. latest_estimate.estimate
    """

    direct_total = astraa_float_or_none(payload.get("total_budget_estimate"))

    if direct_total is not None:
        return direct_total, "total_budget_estimate"

    direct_hard = astraa_float_or_none(payload.get("hard_cost_estimate"))

    if direct_hard is not None:
        return direct_hard, "hard_cost_estimate"

    latest = payload.get("latest_estimate")

    if isinstance(latest, dict):
        estimate_obj = latest.get("estimate")

        if isinstance(estimate_obj, dict):
            nested_estimate = astraa_float_or_none(estimate_obj.get("estimate"))

            if nested_estimate is not None:
                return nested_estimate, "latest_estimate.estimate.estimate"

        flat_estimate = astraa_float_or_none(latest.get("estimate"))

        if flat_estimate is not None:
            return flat_estimate, "latest_estimate.estimate"

    return None, "not_available"


def astraa_build_feedback_record(payload):
    feedback_id = "fb_" + uuid.uuid4().hex

    account_email = astraa_normalize_email(
        payload.get("account_email") or
        payload.get("email") or
        payload.get("checkout_email")
    )

    actual_final_cost = astraa_float_or_none(payload.get("actual_final_cost"))
    estimate_amount, estimate_amount_source = astraa_extract_estimate_amount(payload)

    error_amount = None
    error_percent = None
    estimate_direction = None

    if actual_final_cost is not None and actual_final_cost > 0 and estimate_amount is not None:
        error_amount = estimate_amount - actual_final_cost
        error_percent = (error_amount / actual_final_cost) * 100

        if error_amount > 0:
            estimate_direction = "over_estimated"
        elif error_amount < 0:
            estimate_direction = "under_estimated"
        else:
            estimate_direction = "matched_actual"

    record = {
        "feedback_id": feedback_id,
        "created_at": astraa_now_iso(),

        "account_email": account_email,
        "business_name": payload.get("business_name") or "",
        "selected_tool": payload.get("selected_tool") or "Astraa Estimator",
        "selected_plan": payload.get("selected_plan") or "",
        "selected_price": payload.get("selected_price") or "",

        "project_type": payload.get("project_type") or "",
        "location_market": payload.get("location_market") or "",
        "quality_level": payload.get("quality_level") or "",
        "square_footage": astraa_float_or_none(payload.get("square_footage")),
        "base_rate": astraa_float_or_none(payload.get("base_rate")),
        "bcpi_factor": astraa_float_or_none(payload.get("bcpi_factor")),
        "material_index": astraa_float_or_none(payload.get("material_index")),
        "labor_index": astraa_float_or_none(payload.get("labor_index")),
        "complexity": astraa_float_or_none(payload.get("complexity")),

        "customer_budget": astraa_float_or_none(payload.get("customer_budget")),
        "hard_cost_estimate": astraa_float_or_none(payload.get("hard_cost_estimate")),
        "soft_cost": astraa_float_or_none(payload.get("soft_cost")),
        "contingency": astraa_float_or_none(payload.get("contingency")),
        "total_budget_estimate": astraa_float_or_none(payload.get("total_budget_estimate")),

        "actual_final_cost": actual_final_cost,
        "written_feedback": str(payload.get("written_feedback") or "").strip() or None,
        "customer_rating": payload.get("customer_rating"),
        "was_estimate_useful": payload.get("was_estimate_useful"),

        "estimate_amount_used_for_error": estimate_amount,
        "estimate_amount_source": estimate_amount_source,
        "error_amount": error_amount,
        "error_percent": error_percent,
        "estimate_direction": estimate_direction,

        "latest_estimate": payload.get("latest_estimate"),
        "source": payload.get("source") or "customer_portal_feedback",

        "learning_status": "captured_pending_review"
    }

    return record


@app.route("/api/feedback", methods=["POST"])
def astraa_create_feedback():
    payload = astraa_get_request_json()

    actual_final_cost = astraa_float_or_none(payload.get("actual_final_cost"))
    written_feedback = str(payload.get("written_feedback") or "").strip()

    if (actual_final_cost is None or actual_final_cost <= 0) and not written_feedback:
        return astraa_json_response({
            "success": False,
            "error": "Please provide an actual final cost or written feedback."
        }, 400)

    record = astraa_build_feedback_record(payload)

    records = astraa_load_feedback_db()
    records.append(record)
    astraa_save_feedback_db(records)

    return astraa_json_response({
        "success": True,
        "message": "Feedback captured for Astraa learning review.",
        "feedback": {
            "feedback_id": record["feedback_id"],
            "learning_status": record["learning_status"],
            "actual_final_cost": record["actual_final_cost"],
            "written_feedback": record["written_feedback"],
            "estimate_amount_used_for_error": record["estimate_amount_used_for_error"],
            "error_amount": record["error_amount"],
            "error_percent": record["error_percent"],
            "estimate_direction": record["estimate_direction"]
        }
    })


@app.route("/api/feedback", methods=["GET"])
def astraa_get_feedback():
    email = astraa_normalize_email(astraa_get_query_arg("email"))
    records = astraa_load_feedback_db()

    if email:
        records = [
            r for r in records
            if astraa_normalize_email(r.get("account_email")) == email
        ]

    return astraa_json_response({
        "success": True,
        "count": len(records),
        "feedback": records[-50:]
    })

# -------------------------------------------------------------------
# END ASTRAA FEEDBACK API
# -------------------------------------------------------------------



# -------------------------------------------------------------------
# ASTRAA CALIBRATION SUGGESTIONS API
# Reads captured feedback and produces review-only calibration suggestions.
#
# Important:
# - This does NOT automatically update estimator logic.
# - Suggestions are pending review.
# - Human approval should be required before changing multipliers/base rates.
# -------------------------------------------------------------------

ASTRAA_CALIBRATION_MIN_RECORDS = int(os.getenv("ASTRAA_CALIBRATION_MIN_RECORDS", "3"))
ASTRAA_CALIBRATION_ADJUSTMENT_STRENGTH = float(os.getenv("ASTRAA_CALIBRATION_ADJUSTMENT_STRENGTH", "0.50"))


def astraa_feedback_group_key(record):
    location = record.get("location_market") or "Unknown Market"
    project_type = record.get("project_type") or "Unknown Project Type"
    quality_level = record.get("quality_level") or "Unknown Quality"

    return f"{location}||{project_type}||{quality_level}"


def astraa_split_feedback_key(key):
    parts = key.split("||")

    while len(parts) < 3:
        parts.append("Unknown")

    return {
        "location_market": parts[0],
        "project_type": parts[1],
        "quality_level": parts[2]
    }


def astraa_average(values):
    values = [v for v in values if isinstance(v, (int, float))]

    if not values:
        return None

    return sum(values) / len(values)


def astraa_direction_from_average_error(avg_error):
    if avg_error is None:
        return "unknown"

    if avg_error > 0:
        return "over_estimated"

    if avg_error < 0:
        return "under_estimated"

    return "matched_actual"


def astraa_current_location_multiplier(location_market):
    try:
        return astraa_bc_location_multiplier(location_market)
    except Exception:
        return None


def astraa_suggest_multiplier(location_market, avg_error_percent):
    current = astraa_current_location_multiplier(location_market)

    if current is None or avg_error_percent is None:
        return None

    # If estimates are over actuals by +8%, reduce multiplier partially.
    # If estimates are under actuals by -8%, increase multiplier partially.
    adjustment = 1 - ((avg_error_percent / 100) * ASTRAA_CALIBRATION_ADJUSTMENT_STRENGTH)

    suggested = current * adjustment

    # Guardrails to avoid extreme auto-suggestions.
    suggested = max(0.70, min(1.20, suggested))

    return round(suggested, 4)


def astraa_build_calibration_suggestions():
    records = astraa_load_feedback_db()

    usable = []

    for record in records:
        error_percent = record.get("error_percent")

        if isinstance(error_percent, (int, float)):
            usable.append(record)

    grouped = {}

    for record in usable:
        key = astraa_feedback_group_key(record)
        grouped.setdefault(key, []).append(record)

    suggestions = []
    learning_groups = []

    for key, group_records in grouped.items():
        key_parts = astraa_split_feedback_key(key)
        errors = [r.get("error_percent") for r in group_records if isinstance(r.get("error_percent"), (int, float))]
        avg_error = astraa_average(errors)
        direction = astraa_direction_from_average_error(avg_error)

        location = key_parts["location_market"]
        current_multiplier = astraa_current_location_multiplier(location)
        suggested_multiplier = astraa_suggest_multiplier(location, avg_error)

        item = {
            "location_market": key_parts["location_market"],
            "project_type": key_parts["project_type"],
            "quality_level": key_parts["quality_level"],
            "feedback_count": len(group_records),
            "minimum_required": ASTRAA_CALIBRATION_MIN_RECORDS,
            "average_error_percent": avg_error,
            "direction": direction,
            "current_location_multiplier": current_multiplier,
            "suggested_location_multiplier": suggested_multiplier,
            "status": "pending_review" if len(group_records) >= ASTRAA_CALIBRATION_MIN_RECORDS else "not_enough_feedback",
            "note": ""
        }

        if len(group_records) < ASTRAA_CALIBRATION_MIN_RECORDS:
            item["note"] = (
                "Captured learning signal, but not enough feedback records yet for a calibration suggestion. "
                f"Need at least {ASTRAA_CALIBRATION_MIN_RECORDS} records in this same market/project/quality group."
            )
            learning_groups.append(item)
        else:
            if direction == "over_estimated":
                item["note"] = (
                    "Average feedback indicates Astraa estimates are higher than actuals for this group. "
                    "Suggested multiplier is reduced partially and requires review."
                )
            elif direction == "under_estimated":
                item["note"] = (
                    "Average feedback indicates Astraa estimates are lower than actuals for this group. "
                    "Suggested multiplier is increased partially and requires review."
                )
            else:
                item["note"] = "Average feedback is close to actuals for this group. Review before changing calibration."

            suggestions.append(item)

    return suggestions, learning_groups, len(records), len(usable)


@app.route("/api/calibration/suggestions", methods=["GET"])
def astraa_get_calibration_suggestions():
    suggestions, learning_groups, total_feedback, usable_feedback = astraa_build_calibration_suggestions()

    return astraa_json_response({
        "success": True,
        "total_feedback_records": total_feedback,
        "usable_feedback_records": usable_feedback,
        "minimum_records_required": ASTRAA_CALIBRATION_MIN_RECORDS,
        "suggestions": suggestions,
        "learning_groups": learning_groups,
        "message": (
            "Calibration suggestions are review-only. Astraa should not automatically change estimator logic "
            "without human approval and versioning."
        )
    })

# -------------------------------------------------------------------
# END ASTRAA CALIBRATION SUGGESTIONS API
# -------------------------------------------------------------------



# -------------------------------------------------------------------
# ASTRAA CALIBRATION APPROVAL API
# Turns review-only calibration suggestions into approved calibration
# overrides that can be used by future estimates.
#
# Important:
# - Approval is manual/human-reviewed.
# - Approved records are versioned.
# - Suggestions alone do not change estimator behavior.
# -------------------------------------------------------------------

ASTRAA_APPROVED_CALIBRATION_DB_PATH = Path(
    os.getenv(
        "ASTRAA_APPROVED_CALIBRATION_DB_PATH",
        str(ASTRAA_DATA_DIR / "astraa_approved_calibrations_db.json")
    )
)


def astraa_load_approved_calibrations_db():
    if not ASTRAA_APPROVED_CALIBRATION_DB_PATH.exists():
        return []

    try:
        with ASTRAA_APPROVED_CALIBRATION_DB_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []
    except Exception:
        return []


def astraa_save_approved_calibrations_db(records):
    ASTRAA_APPROVED_CALIBRATION_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    tmp = ASTRAA_APPROVED_CALIBRATION_DB_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, sort_keys=True)

    tmp.replace(ASTRAA_APPROVED_CALIBRATION_DB_PATH)


def astraa_calibration_key(location_market, project_type, quality_level):
    return (
        str(location_market or "").strip().lower(),
        str(project_type or "").strip().lower(),
        str(quality_level or "").strip().lower()
    )


def astraa_find_matching_suggestion(location_market, project_type, quality_level):
    suggestions, learning_groups, total_feedback, usable_feedback = astraa_build_calibration_suggestions()

    target = astraa_calibration_key(location_market, project_type, quality_level)

    for suggestion in suggestions:
        candidate = astraa_calibration_key(
            suggestion.get("location_market"),
            suggestion.get("project_type"),
            suggestion.get("quality_level")
        )

        if candidate == target:
            return suggestion

    return None


def astraa_find_approved_calibration(location_market, project_type="", quality_level=""):
    records = astraa_load_approved_calibrations_db()

    target = astraa_calibration_key(location_market, project_type, quality_level)

    approved_matches = []

    for record in records:
        if record.get("status") != "approved":
            continue

        candidate = astraa_calibration_key(
            record.get("location_market"),
            record.get("project_type"),
            record.get("quality_level")
        )

        if candidate == target:
            approved_matches.append(record)

    if not approved_matches:
        return None

    approved_matches.sort(key=lambda r: r.get("approved_at") or "", reverse=True)

    return approved_matches[0]


def astraa_get_effective_location_multiplier(location_market, project_type="", quality_level=""):
    approved = astraa_find_approved_calibration(location_market, project_type, quality_level)

    if approved and approved.get("approved_multiplier") is not None:
        return float(approved["approved_multiplier"])

    return astraa_bc_location_multiplier(location_market)


@app.route("/api/calibration/approve", methods=["POST"])
def astraa_approve_calibration():
    payload = astraa_get_request_json()

    location_market = payload.get("location_market")
    project_type = payload.get("project_type")
    quality_level = payload.get("quality_level")

    approved_multiplier = astraa_float_or_none(payload.get("approved_multiplier"))
    approved_by = str(payload.get("approved_by") or "Astraa Admin").strip()
    reason = str(payload.get("reason") or "").strip()

    if not location_market or not project_type or not quality_level:
        return astraa_json_response({
            "success": False,
            "error": "location_market, project_type, and quality_level are required."
        }, 400)

    if approved_multiplier is None:
        return astraa_json_response({
            "success": False,
            "error": "approved_multiplier is required and must be numeric."
        }, 400)

    if approved_multiplier < 0.70 or approved_multiplier > 1.20:
        return astraa_json_response({
            "success": False,
            "error": "approved_multiplier must be between 0.70 and 1.20."
        }, 400)

    suggestion = astraa_find_matching_suggestion(
        location_market,
        project_type,
        quality_level
    )

    if not suggestion:
        return astraa_json_response({
            "success": False,
            "error": "No pending calibration suggestion found for this market/project/quality group. Make sure minimum feedback threshold has been reached."
        }, 404)

    calibration_id = "cal_" + uuid.uuid4().hex

    old_multiplier = suggestion.get("current_location_multiplier")
    suggested_multiplier = suggestion.get("suggested_location_multiplier")

    record = {
        "calibration_id": calibration_id,
        "status": "approved",
        "created_at": astraa_now_iso(),
        "approved_at": astraa_now_iso(),
        "approved_by": approved_by,

        "location_market": location_market,
        "project_type": project_type,
        "quality_level": quality_level,

        "old_multiplier": old_multiplier,
        "suggested_multiplier": suggested_multiplier,
        "approved_multiplier": approved_multiplier,

        "average_error_percent": suggestion.get("average_error_percent"),
        "direction": suggestion.get("direction"),
        "feedback_count": suggestion.get("feedback_count"),
        "minimum_required": suggestion.get("minimum_required"),

        "reason": reason or suggestion.get("note") or "Approved calibration adjustment.",
        "source": "manual_calibration_approval",
        "version_label": (
            str(location_market).replace(" ", "_").replace("/", "").lower()
            + "_"
            + str(project_type).replace(" ", "_").lower()
            + "_"
            + str(quality_level).replace(" ", "_").lower()
        )
    }

    records = astraa_load_approved_calibrations_db()
    records.append(record)
    astraa_save_approved_calibrations_db(records)

    return astraa_json_response({
        "success": True,
        "message": "Calibration approved and versioned.",
        "approved_calibration": record
    })


@app.route("/api/calibration/approved", methods=["GET"])
def astraa_get_approved_calibrations():
    records = astraa_load_approved_calibrations_db()

    location_market = astraa_get_query_arg("location_market")
    project_type = astraa_get_query_arg("project_type")
    quality_level = astraa_get_query_arg("quality_level")

    if location_market:
        records = [
            r for r in records
            if str(r.get("location_market") or "").lower() == str(location_market).lower()
        ]

    if project_type:
        records = [
            r for r in records
            if str(r.get("project_type") or "").lower() == str(project_type).lower()
        ]

    if quality_level:
        records = [
            r for r in records
            if str(r.get("quality_level") or "").lower() == str(quality_level).lower()
        ]

    return astraa_json_response({
        "success": True,
        "count": len(records),
        "approved_calibrations": records[-100:]
    })

# -------------------------------------------------------------------
# END ASTRAA CALIBRATION APPROVAL API
# -------------------------------------------------------------------



# -------------------------------------------------------------------
# ASTRAA ESTIMATE CREDIT PACK API
# Allows additional estimate credits to be added to an account.
#
# Product rule:
# - $10 CAD = 10 extra estimates
# - Available to Trial, Basic, Professional, and custom users
#
# Soft-launch note:
# - This endpoint adds credits directly for testing/admin workflow.
# - Production should call this only after verified Moneris payment.
# -------------------------------------------------------------------

def astraa_add_estimate_credits_to_record(record, credits, amount_cad, source="manual_credit_add"):
    credits = int(credits or 0)

    if credits <= 0:
        raise ValueError("credits must be greater than zero")

    current_limit = int(record.get("estimate_limit") or 0)
    current_extra = int(record.get("extra_estimate_credits_total") or 0)

    record["estimate_limit"] = current_limit + credits
    record["extra_estimate_credits_total"] = current_extra + credits

    packs = record.get("estimate_credit_packs")

    if not isinstance(packs, list):
        packs = []

    packs.append({
        "created_at": astraa_now_iso(),
        "credits": credits,
        "amount_cad": amount_cad,
        "source": source,
        "note": "$10 CAD estimate pack = 10 extra estimates"
    })

    record["estimate_credit_packs"] = packs
    record["updated_at"] = astraa_now_iso()

    return record


@app.route("/api/account/estimate-credits/add", methods=["POST"])
# ASTRAA_ESTIMATE_CREDITS_STORAGE_WRAPPER_ADOPTION_V1
def astraa_add_estimate_credits():
    payload = astraa_get_request_json()

    email = astraa_normalize_email(payload.get("email"))
    credits = int(payload.get("credits") or 10)
    amount_cad = float(payload.get("amount_cad") or 10.00)
    source = payload.get("source") or "manual_credit_add"

    if not email:
        return astraa_json_response({
            "success": False,
            "error": "Missing email."
        }, 400)

    # ASTRAA_ESTIMATE_CREDITS_TUPLE_FIX_V1
    usage_lookup = astraa_get_usage_record(email)

    if isinstance(usage_lookup, tuple):
        db, record = usage_lookup
    else:
        db = astraa_storage_load_usage_db()
        record = usage_lookup

    if not record:
        record, error = astraa_create_or_update_account_usage(
            email=email,
            selected_tool=payload.get("selected_tool") or "Astraa Estimator",
            selected_plan=payload.get("selected_plan") or "Trial",
            selected_price=payload.get("selected_price") or "$0 / 15 days",
            payment_status=payload.get("payment_status") or "active",
            business_name=payload.get("business_name") or "",
            industry=payload.get("industry") or ""
        )

        if error:
            return astraa_json_response({
                "success": False,
                "error": error
            }, 400)

    try:
        record = astraa_add_estimate_credits_to_record(
            record=record,
            credits=credits,
            amount_cad=amount_cad,
            source=source
        )
    except Exception as error:
        return astraa_json_response({
            "success": False,
            "error": str(error)
        }, 400)

    db = astraa_storage_load_usage_db()
    db[astraa_account_key(email)] = record
    astraa_storage_save_usage_db(db)

    return astraa_json_response({
        "success": True,
        "message": f"Added {credits} extra estimate credits.",
        "usage": astraa_usage_summary(record),
        "credit_pack": {
            "credits": credits,
            "amount_cad": amount_cad,
            "price_label": "$10 CAD / 10 extra estimates"
        }
    })

# -------------------------------------------------------------------
# END ASTRAA ESTIMATE CREDIT PACK API
# -------------------------------------------------------------------




# ============================================================
# ASTRAA GATEWAY — Workspace Tool QA Test Route
# ============================================================

from flask import request, jsonify
from datetime import datetime, timezone
import html
import re

ASTRAA_ALLOWED_TEST_EMAIL = "astraa.live.test@astraasystems.com"

ASTRAA_ALLOWED_TOOLS = {
    "estimator",
    "expense",
    "finance",
    "operations",
    "commerce",
    "data",
    "inference",
    "distribution",
    "vault",
}

def astraa_safe_float(value, default=0):
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except Exception:
        return default

def astraa_sanitize(value):
    if value is None:
        return ""

    if isinstance(value, (int, float, bool)):
        return value

    if isinstance(value, str):
        value = value.strip()
        value = html.escape(value)
        value = re.sub(r"(?i)<script.*?>.*?</script>", "", value)
        value = re.sub(r"(?i)javascript:", "", value)
        value = re.sub(r"(?i)onerror\s*=", "", value)
        value = re.sub(r"(?i)onclick\s*=", "", value)
        return value[:5000]

    if isinstance(value, list):
        return [astraa_sanitize(v) for v in value]

    if isinstance(value, dict):
        return {str(astraa_sanitize(k)): astraa_sanitize(v) for k, v in value.items()}

    return str(value)

def astraa_validate_payload(payload):
    errors = []

    if not isinstance(payload, dict):
        return ["Payload must be a JSON object."]

    tenant = payload.get("tenant_context", {})
    tool = payload.get("tool", {})
    inputs = payload.get("inputs", {})

    if tenant.get("test_email") != ASTRAA_ALLOWED_TEST_EMAIL:
        errors.append("Invalid test tenant email.")

    if tenant.get("plan") not in ["Trial", "Basic", "Professional", "Custom"]:
        errors.append("Invalid or missing plan.")

    if tenant.get("access") != "Full internal test mode":
        errors.append("Invalid Workspace test access.")

    if tool.get("key") not in ASTRAA_ALLOWED_TOOLS:
        errors.append(f"Unsupported tool key: {tool.get('key')}")

    if not isinstance(inputs, dict):
        errors.append("Inputs must be a JSON object.")

    return errors

def astraa_tool_response(tool_key, inputs):
    if tool_key == "estimator":
        base = astraa_safe_float(inputs.get("base_cost"))

        # Multipliers default to 1.0. These are internal QA factors and can later map to
        # the production Estimator engine tables.
        material_multiplier = astraa_safe_float(inputs.get("material_multiplier"), 1)
        labor_multiplier = astraa_safe_float(inputs.get("labor_multiplier"), 1)
        location_multiplier = astraa_safe_float(inputs.get("location_multiplier"), 1)
        quality_multiplier = astraa_safe_float(inputs.get("quality_multiplier"), 1)
        access_multiplier = astraa_safe_float(inputs.get("access_multiplier"), 1)
        complexity_factor = astraa_safe_float(inputs.get("complexity_factor"), 1)
        collaboration_factor = astraa_safe_float(inputs.get("collaboration_factor"), 1)
        rush_factor = astraa_safe_float(inputs.get("rush_factor"), 1)

        # Rates can be supplied as either 0.10 or 10.
        overhead_rate = astraa_safe_float(inputs.get("overhead_rate"), 0)
        contingency_rate = astraa_safe_float(inputs.get("contingency_rate"), 0)
        tax_rate = astraa_safe_float(inputs.get("tax_rate"), 0)

        if overhead_rate > 1:
            overhead_rate = overhead_rate / 100
        if contingency_rate > 1:
            contingency_rate = contingency_rate / 100
        if tax_rate > 1:
            tax_rate = tax_rate / 100

        adjusted_subtotal = (
            base
            * material_multiplier
            * labor_multiplier
            * location_multiplier
            * quality_multiplier
            * access_multiplier
            * complexity_factor
            * collaboration_factor
            * rush_factor
        )

        overhead_amount = adjusted_subtotal * overhead_rate
        contingency_amount = adjusted_subtotal * contingency_rate
        taxable_subtotal = adjusted_subtotal + overhead_amount + contingency_amount
        tax_amount = taxable_subtotal * tax_rate
        estimated_total = taxable_subtotal + tax_amount

        return {
            "tool": "Astraa Estimator",
            "pipeline": ["Astraa Gateway", "Estimator Engine", "Operations", "Finance", "Vault"],
            "result": {
                "base_cost": round(base, 2),
                "adjusted_subtotal": round(adjusted_subtotal, 2),
                "overhead_amount": round(overhead_amount, 2),
                "contingency_amount": round(contingency_amount, 2),
                "tax_amount": round(tax_amount, 2),
                "estimated_total": round(estimated_total, 2),
                "factor_breakdown": {
                    "material_multiplier": material_multiplier,
                    "labor_multiplier": labor_multiplier,
                    "location_multiplier": location_multiplier,
                    "quality_multiplier": quality_multiplier,
                    "access_multiplier": access_multiplier,
                    "complexity_factor": complexity_factor,
                    "collaboration_factor": collaboration_factor,
                    "rush_factor": rush_factor,
                    "overhead_rate": overhead_rate,
                    "contingency_rate": contingency_rate,
                    "tax_rate": tax_rate
                },
                "plan_rule": "Professional includes 120 estimates per month.",
                "extra_pack_rule": "$10 CAD per 10 additional estimates.",
                "review_note": "Planning-grade estimate output. Review before customer use. Production Estimator tables can replace QA factor values later."
            }
        }

    if tool_key == "expense":
        amount = astraa_safe_float(inputs.get("amount"))
        return {
            "tool": "Astraa Expense",
            "pipeline": ["Astraa Gateway", "Expense Tool", "Finance", "Vault"],
            "result": {
                "expense_amount": round(amount, 2),
                "category": inputs.get("category", ""),
                "finance_handoff": True,
                "review_note": "Expense summary ready for Finance visibility testing."
            }
        }

    if tool_key == "finance":
        revenue = astraa_safe_float(inputs.get("revenue"))
        original_contract_sum = astraa_safe_float(inputs.get("original_contract_sum"))
        change_orders = astraa_safe_float(inputs.get("change_orders"))
        work_completed_to_date = astraa_safe_float(inputs.get("work_completed_to_date"))
        materials_presently_stored = astraa_safe_float(inputs.get("materials_presently_stored"))
        retainage_rate = astraa_safe_float(inputs.get("retainage_rate"), 10)
        labor_hours = astraa_safe_float(inputs.get("labor_hours"))
        burden_rate = astraa_safe_float(inputs.get("burden_rate"))
        material_cost = astraa_safe_float(inputs.get("material_cost"))
        fleet_expenses = astraa_safe_float(inputs.get("fleet_expenses"))
        gross_sales = astraa_safe_float(inputs.get("gross_sales"))
        royalty_rate = astraa_safe_float(inputs.get("royalty_rate"), 6)
        restricted_fund_amount = astraa_safe_float(inputs.get("restricted_fund_amount"))
        requested_expense_amount = astraa_safe_float(inputs.get("requested_expense_amount"))

        if retainage_rate > 1:
            retainage_rate = retainage_rate / 100
        if royalty_rate > 1:
            royalty_rate = royalty_rate / 100

        province = str(inputs.get("tax_region", "BC")).upper().strip()
        tax_rules = {
            "BC": {"gst": 0.05, "pst": 0.07, "hst": 0.0, "label": "BC GST/PST split"},
            "AB": {"gst": 0.05, "pst": 0.0, "hst": 0.0, "label": "Alberta GST only"},
            "ON": {"gst": 0.0, "pst": 0.0, "hst": 0.13, "label": "Ontario HST"},
            "NB": {"gst": 0.0, "pst": 0.0, "hst": 0.15, "label": "Atlantic HST"},
            "NS": {"gst": 0.0, "pst": 0.0, "hst": 0.15, "label": "Atlantic HST"},
            "NL": {"gst": 0.0, "pst": 0.0, "hst": 0.15, "label": "Atlantic HST"},
            "PE": {"gst": 0.0, "pst": 0.0, "hst": 0.15, "label": "Atlantic HST"},
        }
        tax_rule = tax_rules.get(province, tax_rules["BC"])

        revised_contract_sum = original_contract_sum + change_orders
        progress_base = work_completed_to_date + materials_presently_stored
        retainage_amount = progress_base * retainage_rate
        amount_due_before_tax = max(progress_base - retainage_amount, 0)

        gst_amount = amount_due_before_tax * tax_rule["gst"]
        pst_amount = amount_due_before_tax * tax_rule["pst"]
        hst_amount = amount_due_before_tax * tax_rule["hst"]
        invoice_total = amount_due_before_tax + gst_amount + pst_amount + hst_amount

        labor_cost = labor_hours * burden_rate
        live_profit = revenue - labor_cost - material_cost - fleet_expenses
        royalty_amount = gross_sales * royalty_rate
        nonprofit_allowed = requested_expense_amount <= restricted_fund_amount if restricted_fund_amount else True

        return {
            "tool": "Astraa Finance",
            "pipeline": ["Astraa Gateway", "Finance Tool", "Expense", "Operations", "Distribution", "Vault"],
            "result": {
                "progress_billing": {
                    "original_contract_sum": round(original_contract_sum, 2),
                    "change_orders": round(change_orders, 2),
                    "revised_contract_sum": round(revised_contract_sum, 2),
                    "work_completed_to_date": round(work_completed_to_date, 2),
                    "materials_presently_stored": round(materials_presently_stored, 2),
                    "retainage_rate": retainage_rate,
                    "retainage_amount": round(retainage_amount, 2),
                    "amount_due_before_tax": round(amount_due_before_tax, 2)
                },
                "canadian_tax_matrix": {
                    "province": province,
                    "rule": tax_rule["label"],
                    "gst_amount": round(gst_amount, 2),
                    "pst_amount": round(pst_amount, 2),
                    "hst_amount": round(hst_amount, 2),
                    "invoice_total": round(invoice_total, 2)
                },
                "contractor_profitability": {
                    "labor_cost": round(labor_cost, 2),
                    "material_cost": round(material_cost, 2),
                    "fleet_expenses": round(fleet_expenses, 2),
                    "live_profit": round(live_profit, 2)
                },
                "franchise_royalty": {
                    "gross_sales": round(gross_sales, 2),
                    "royalty_rate": royalty_rate,
                    "royalty_amount": round(royalty_amount, 2)
                },
                "nonprofit_fund_control": {
                    "restricted_fund_amount": round(restricted_fund_amount, 2),
                    "requested_expense_amount": round(requested_expense_amount, 2),
                    "allowed_by_restriction_check": nonprofit_allowed
                },
                "audit_log_ready": True,
                "payment_gateway_ready": True,
                "review_note": "Finance QA covers progress billing, tax matrix, audit logs, sector-specific capital tracking, and invoice/payment readiness. Planning visibility only; not accounting, tax, legal, or investment advice."
            }
        }

    if tool_key == "operations":
        required_certification = str(inputs.get("required_certification", "")).strip()
        worker_certification = str(inputs.get("worker_certification", "")).strip()
        worker_name = inputs.get("worker_name", "")
        task = inputs.get("task", "")
        owner = inputs.get("owner", "")
        due_date = inputs.get("due_date", "")
        priority = inputs.get("priority", "")
        blocker = inputs.get("blocker", "")
        tenant_level = inputs.get("tenant_level", "Branch")
        branch_id = inputs.get("branch_id", "")
        staging_capacity_sqm = astraa_safe_float(inputs.get("staging_capacity_sqm"))
        required_footprint_sqm = astraa_safe_float(inputs.get("required_footprint_sqm"))
        planned_arrival = inputs.get("planned_arrival", "")
        actual_arrival = inputs.get("actual_arrival", "")
        labor_hours = astraa_safe_float(inputs.get("labor_hours"))
        fuel_burn_liters = astraa_safe_float(inputs.get("fuel_burn_liters"))
        demurrage_minutes = astraa_safe_float(inputs.get("demurrage_minutes"))
        asset_depreciation_cad = astraa_safe_float(inputs.get("asset_depreciation_cad"))
        milestone_id = inputs.get("milestone_id", "")
        project_id = inputs.get("project_id", "")
        tenant_id = inputs.get("tenant_id", "")

        certification_match = bool(required_certification) and required_certification == worker_certification
        staging_ok = required_footprint_sqm <= staging_capacity_sqm if staging_capacity_sqm else True
        suggested_arrival = planned_arrival if staging_ok else "Shift delivery slot / staging conflict detected"

        operational_to_finance_payload = {
            "transactionId": inputs.get("transaction_id", "TXN-QA-OPS-001"),
            "tenantId": tenant_id or "ASTRAA-QA-TENANT",
            "projectId": project_id or "ASTRAA-QA-PROJECT",
            "milestoneId": milestone_id or "ASTRAA-QA-MILESTONE",
            "verification": {
                "status": "VERIFIED",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "method": inputs.get("verification_method", "QA_FIELD_UPDATE_PROTOCOL")
            },
            "operationalMetrics": {
                "totalLaborHours": labor_hours,
                "laborBurdenClass": inputs.get("labor_burden_class", "QA_BURDEN_CLASS"),
                "materialsConsumed": [
                    {
                        "item": inputs.get("material_item", "QA_MATERIAL"),
                        "quantity": astraa_safe_float(inputs.get("material_quantity")),
                        "unit": inputs.get("material_unit", "UNITS")
                    }
                ]
            },
            "liveLogisticsOverhead": {
                "fuelBurnLiters": fuel_burn_liters,
                "demurrageMinutes": demurrage_minutes,
                "assetDepreciationCAD": asset_depreciation_cad
            }
        }

        return {
            "tool": "Astraa Operations",
            "pipeline": ["Astraa Gateway", "Operations Tool", "Distribution", "Expense", "Finance", "Vault"],
            "result": {
                "crew_dispatch": {
                    "task": task,
                    "worker_name": worker_name,
                    "owner": owner,
                    "due_date": due_date,
                    "priority": priority,
                    "blocker": blocker,
                    "required_certification": required_certification,
                    "worker_certification": worker_certification,
                    "certification_match": certification_match,
                    "dispatch_allowed": certification_match if required_certification else True
                },
                "multi_tenant_isolation": {
                    "tenant_level": tenant_level,
                    "branch_id": branch_id,
                    "hq_visibility": tenant_level.upper() in ["HQ", "CORPORATE"],
                    "branch_sandboxed": tenant_level.upper() not in ["HQ", "CORPORATE"]
                },
                "staging_yard_control": {
                    "staging_capacity_sqm": staging_capacity_sqm,
                    "required_footprint_sqm": required_footprint_sqm,
                    "staging_ok": staging_ok,
                    "planned_arrival": planned_arrival,
                    "suggested_arrival_action": suggested_arrival
                },
                "sla_tracking": {
                    "planned_arrival": planned_arrival,
                    "actual_arrival": actual_arrival,
                    "photo_proof_expected": True,
                    "gps_checkin_expected": True
                },
                "field_update_protocol": {
                    "micro_payload_ready": True,
                    "status": "Ready for Astraa Gateway push"
                },
                "operations_to_finance_handshake": operational_to_finance_payload,
                "review_note": "Operations QA covers crew dispatch, certification checks, tenant isolation, staging capacity, field updates, SLA tracking, and Finance handoff."
            }
        }

    if tool_key == "commerce":
        return {
            "tool": "Astraa Commerce",
            "pipeline": ["Astraa Gateway", "Commerce Tool", "Finance", "Vault"],
            "result": {
                "offer_type": inputs.get("offer_type", ""),
                "catalog_need": inputs.get("catalog_need", ""),
                "transaction_note": inputs.get("transaction_note", ""),
                "review_note": "Commerce is QA-ready and customer access remains controlled."
            }
        }

    if tool_key == "data":
        return {
            "tool": "Astraa Data",
            "pipeline": ["Astraa Gateway", "Data Tool", "Vault"],
            "result": {
                "data_source": inputs.get("data_source", ""),
                "report_need": inputs.get("report_need", ""),
                "record_type": inputs.get("record_type", ""),
                "review_note": "Data QA route prepared for reporting and Vault handoff."
            }
        }

    if tool_key == "inference":
        return {
            "tool": "Astraa Inference",
            "pipeline": ["Astraa Gateway", "Inference Tool", "Vault"],
            "result": {
                "scenario": inputs.get("scenario", ""),
                "assumptions": inputs.get("assumptions", ""),
                "risk_note": inputs.get("risk_note", ""),
                "review_note": "Decision-support output only. Requires review."
            }
        }

    if tool_key == "distribution":
        return {
            "tool": "Astraa Distribution",
            "pipeline": ["Astraa Gateway", "Distribution Utility", "Expense", "Finance", "Vault"],
            "result": {
                "origin_node": inputs.get("origin_node", ""),
                "destination": inputs.get("destination", ""),
                "delivery_window": inputs.get("delivery_window", ""),
                "review_note": "Distribution QA route prepared for route/inventory workflow."
            }
        }

    if tool_key == "vault":
        return {
            "tool": "Astraa Vault",
            "pipeline": ["Astraa Gateway", "Vault"],
            "result": {
                "record_type": inputs.get("record_type", ""),
                "access_level": inputs.get("access_level", ""),
                "storage_group": inputs.get("storage_group", ""),
                "review_note": "Vault QA route prepared for secure record storage."
            }
        }

    return {
        "tool": "Unknown",
        "pipeline": ["Astraa Gateway"],
        "result": {}
    }

@app.post("/api/astraa/workspace/tool-test")
def astraa_workspace_tool_test():
    raw_payload = request.get_json(silent=True)

    if raw_payload is None:
        return jsonify({
            "status": "rejected",
            "gateway": "Astraa Gateway",
            "errors": ["Invalid or missing JSON payload."]
        }), 400

    payload = astraa_sanitize(raw_payload)
    errors = astraa_validate_payload(payload)

    if errors:
        return jsonify({
            "status": "rejected",
            "gateway": "Astraa Gateway",
            "errors": errors
        }), 400

    tool_key = payload.get("tool", {}).get("key")
    inputs = payload.get("inputs", {})

    response = astraa_tool_response(tool_key, inputs)

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "tenant_context": {
            "plan": payload.get("tenant_context", {}).get("plan"),
            "access": payload.get("tenant_context", {}).get("access"),
            "isolated": True
        },
        "gateway_controls": {
            "payload_sanitized": True,
            "schema_validated": True,
            "tenant_isolation_checked": True,
            "vault_route_ready": True,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        },
        **response
    }), 200




# ============================================================
# ASTRAA GATEWAY — Estimator Execution Blueprint Route
# Purpose:
#   Turns an approved estimate into structured Operations,
#   Distribution, Finance, Commerce, and Vault-ready payloads.
# ============================================================

@app.post("/api/astraa/estimator/execution-blueprint")
def astraa_estimator_execution_blueprint():
    raw_payload = request.get_json(silent=True)

    if raw_payload is None:
        return jsonify({
            "status": "rejected",
            "gateway": "Astraa Gateway",
            "errors": ["Invalid or missing JSON payload."]
        }), 400

    payload = astraa_sanitize(raw_payload)

    tenant = payload.get("tenant_context", {})
    inputs = payload.get("inputs", {})

    errors = []

    if tenant.get("test_email") != ASTRAA_ALLOWED_TEST_EMAIL:
        errors.append("Invalid test tenant email.")

    if tenant.get("plan") not in ["Trial", "Basic", "Professional", "Custom"]:
        errors.append("Invalid or missing plan.")

    if tenant.get("access") != "Full internal test mode":
        errors.append("Invalid Workspace test access.")

    if errors:
        return jsonify({
            "status": "rejected",
            "gateway": "Astraa Gateway",
            "errors": errors
        }), 400

    tenant_id = inputs.get("tenant_id") or "ASTRAA-QA-TENANT"
    project_id = inputs.get("project_id") or "PROJ-QA-ESTIMATOR"
    estimate_id = inputs.get("estimate_id") or "EST-QA-001"
    project_name = inputs.get("project_name") or "Astraa QA Project"
    project_location = inputs.get("project_location") or "Burnaby, BC"
    tax_region = str(inputs.get("tax_region") or "BC").upper()

    base_cost = astraa_safe_float(inputs.get("base_cost"))
    material_multiplier = astraa_safe_float(inputs.get("material_multiplier"), 1)
    labor_multiplier = astraa_safe_float(inputs.get("labor_multiplier"), 1)
    location_multiplier = astraa_safe_float(inputs.get("location_multiplier"), 1)
    complexity_factor = astraa_safe_float(inputs.get("complexity_factor"), 1)
    contingency_rate = astraa_safe_float(inputs.get("contingency_rate"), 7.5)

    if contingency_rate > 1:
        contingency_rate = contingency_rate / 100

    adjusted_budget = (
        base_cost
        * material_multiplier
        * labor_multiplier
        * location_multiplier
        * complexity_factor
    )

    contingency_amount = adjusted_budget * contingency_rate
    execution_budget = adjusted_budget + contingency_amount

    material_profile = inputs.get("material_profile") or "General materials"
    project_scope = inputs.get("project_scope") or "General project scope"
    delivery_window = inputs.get("delivery_window") or "TBD"
    milestone_name = inputs.get("milestone_name") or "Phase 1 - Execution Start"

    operations_blueprint = {
        "tool": "Astraa Operations",
        "payloadType": "OPERATIONS_BLUEPRINT_FROM_ESTIMATE",
        "tenantId": tenant_id,
        "projectId": project_id,
        "estimateId": estimate_id,
        "projectName": project_name,
        "baselineTasks": [
            {
                "taskId": "TASK-EST-001",
                "title": "Review approved estimate scope",
                "ownerRole": "Project Coordinator",
                "status": "Ready"
            },
            {
                "taskId": "TASK-EST-002",
                "title": "Schedule crew and subcontractor requirements",
                "ownerRole": "Operations Manager",
                "status": "Ready"
            },
            {
                "taskId": "TASK-EST-003",
                "title": "Confirm staging yard capacity and receiving windows",
                "ownerRole": "Site Coordinator",
                "status": "Ready"
            }
        ],
        "crewTargets": {
            "laborMultiplier": labor_multiplier,
            "complexityFactor": complexity_factor,
            "certificationCheckRequired": True
        },
        "stagingRequirements": {
            "materialProfile": material_profile,
            "deliveryWindow": delivery_window,
            "siteLocation": project_location
        }
    }

    distribution_blueprint = {
        "tool": "Astraa Distribution",
        "payloadType": "DISTRIBUTION_BLUEPRINT_FROM_ESTIMATE",
        "tenantId": tenant_id,
        "projectId": project_id,
        "estimateId": estimate_id,
        "originNode": inputs.get("origin_node") or "Supplier / Yard TBD",
        "destination": project_location,
        "materialProfile": material_profile,
        "deliveryWindow": delivery_window,
        "capacityConstraints": {
            "requiresRoutePreview": True,
            "requiresStagingCapacityCheck": True,
            "requiresDemurrageRiskCheck": True
        }
    }

    finance_blueprint = {
        "tool": "Astraa Finance",
        "payloadType": "FINANCE_BLUEPRINT_FROM_ESTIMATE",
        "tenantId": tenant_id,
        "projectId": project_id,
        "estimateId": estimate_id,
        "taxRegion": tax_region,
        "contractBudget": round(execution_budget, 2),
        "adjustedBudget": round(adjusted_budget, 2),
        "contingencyAmount": round(contingency_amount, 2),
        "milestones": [
            {
                "milestoneId": "MILESTONE-001",
                "name": milestone_name,
                "billingType": "percentage_of_completion",
                "plannedBillingPercent": 25,
                "status": "Draft"
            }
        ],
        "progressBillingReady": True,
        "reviewNote": "Finance blueprint is planning-grade and must be reviewed before issuing invoices."
    }

    commerce_blueprint = {
        "tool": "Astraa Commerce",
        "payloadType": "COMMERCE_BLUEPRINT_FROM_ESTIMATE",
        "tenantId": tenant_id,
        "projectId": project_id,
        "estimateId": estimate_id,
        "customerApprovalFlow": "Draft approval required before payment request.",
        "billingRailStatus": "Ready for future payment/invoice workflow",
        "paymentGatewayAction": "Do not charge automatically from QA blueprint."
    }

    vault_record = {
        "vaultRecordId": "VAULT-EST-QA-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "recordType": "ESTIMATOR_EXECUTION_BLUEPRINT",
        "tenantId": tenant_id,
        "projectId": project_id,
        "estimateId": estimate_id,
        "sourceTool": "Astraa Estimator",
        "sourceGateway": "Astraa Gateway",
        "visibility": "tenant_private",
        "zeroKnowledgeReady": True,
        "linkedPayloads": {
            "operations": operations_blueprint["payloadType"],
            "distribution": distribution_blueprint["payloadType"],
            "finance": finance_blueprint["payloadType"],
            "commerce": commerce_blueprint["payloadType"]
        },
        "storedObjects": [
            "estimate_summary",
            "operations_blueprint",
            "distribution_blueprint",
            "finance_blueprint",
            "commerce_blueprint"
        ],
        "audit": {
            "payloadSanitized": True,
            "schemaValidated": True,
            "tenantIsolationChecked": True,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
    }

    activity_events = [
        {
            "eventType": "EVENT_ESTIMATE_BLUEPRINT_GENERATED",
            "tool": "estimator",
            "summary": "Estimator generated execution blueprint for Operations, Distribution, Finance, Commerce, and Vault."
        },
        {
            "eventType": "EVENT_OPERATIONS_BLUEPRINT_READY",
            "tool": "operations",
            "summary": "Operations baseline task and staging payload generated."
        },
        {
            "eventType": "EVENT_DISTRIBUTION_BLUEPRINT_READY",
            "tool": "distribution",
            "summary": "Distribution route and delivery-prep payload generated."
        },
        {
            "eventType": "EVENT_FINANCE_BLUEPRINT_READY",
            "tool": "finance",
            "summary": "Finance progress billing draft payload generated."
        },
        {
            "eventType": "EVENT_VAULT_RECORD_READY",
            "tool": "vault",
            "summary": "Vault estimator execution blueprint record prepared."
        }
    ]

    # ASTRAA_ESTIMATOR_BLUEPRINT_CORE_OS_COMMIT_V1
    # Connect this execution blueprint into the Astraa Core OS in-memory stores.
    # This turns the Estimator route from a standalone response into a Core OS event.
    core_os_commit = {
        "entityCreated": None,
        "vaultRecordStored": None,
        "eventPublished": None,
        "activityWritten": []
    }

    try:
        # 1. Create/update project entity in Common Data Model store.
        core_project_entity = {
            "entityId": "PROJECT-" + project_id,
            "entityType": "project",
            "tenantId": tenant_id,
            "projectId": project_id,
            "name": project_name,
            "sector": inputs.get("sector") or "contractor",
            "location": project_location,
            "data": {
                "source": "Estimator Execution Blueprint",
                "estimateId": estimate_id,
                "executionBudget": round(execution_budget, 2),
                "materialProfile": material_profile,
                "projectScope": project_scope,
                "connectedTools": ["estimator", "operations", "distribution", "finance", "commerce", "vault"]
            },
            "createdAt": astraa_core_now(),
            "source": "Astraa Gateway"
        }

        core_project_entity, entity_action = astraa_core_upsert_entity(core_project_entity)
        core_os_commit["entityCreated"] = core_project_entity
        core_os_commit["entityAction"] = entity_action

        core_os_commit["activityWritten"].append(
            astraa_core_write_activity(
                "EVENT_CORE_ENTITY_CREATED",
                tenant_id,
                project_id,
                "estimator",
                "Estimator execution blueprint " + entity_action + " project entity.",
                {
                    "entityId": core_project_entity["entityId"],
                    "estimateId": estimate_id,
                    "action": entity_action
                }
            )
        )

        # 2. Store Vault record in Core OS Vault store.
        vault_record, vault_action = astraa_core_upsert_vault_record(vault_record)
        core_os_commit["vaultRecordStored"] = vault_record
        core_os_commit["vaultRecordAction"] = vault_action

        core_os_commit["activityWritten"].append(
            astraa_core_write_activity(
                "EVENT_CORE_VAULT_RECORD_CREATED",
                tenant_id,
                project_id,
                "vault",
                "Estimator execution blueprint " + vault_action + " Vault record.",
                {
                    "vaultRecordId": vault_record.get("vaultRecordId"),
                    "estimateId": estimate_id,
                    "action": vault_action
                }
            )
        )

        # 3. Publish Core OS event.
        core_event = {
            "eventId": astraa_core_id("EVT"),
            "eventType": "EVENT_ESTIMATE_BLUEPRINT_GENERATED",
            "tenantId": tenant_id,
            "projectId": project_id,
            "tool": "estimator",
            "payload": {
                "estimateId": estimate_id,
                "projectName": project_name,
                "executionBudget": round(execution_budget, 2),
                "spawnedPayloads": {
                    "operations": operations_blueprint.get("payloadType"),
                    "distribution": distribution_blueprint.get("payloadType"),
                    "finance": finance_blueprint.get("payloadType"),
                    "commerce": commerce_blueprint.get("payloadType"),
                    "vaultRecord": vault_record.get("vaultRecordId")
                }
            },
            "timestamp": astraa_core_now(),
            "source": "Astraa Gateway"
        }

        ASTRAA_CORE_EVENTS.append(core_event)
        astraa_core_save_store()
        core_os_commit["eventPublished"] = core_event

        core_os_commit["activityWritten"].append(
            astraa_core_write_activity(
                "EVENT_ESTIMATE_BLUEPRINT_GENERATED",
                tenant_id,
                project_id,
                "estimator",
                "Estimator generated execution blueprint and connected it to Core OS.",
                {
                    "eventId": core_event["eventId"],
                    "estimateId": estimate_id,
                    "vaultRecordId": vault_record.get("vaultRecordId")
                }
            )
        )

    except Exception as core_error:
        core_os_commit["error"] = str(core_error)


    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "route": "/api/astraa/estimator/execution-blueprint",
        "tenant_context": {
            "plan": tenant.get("plan"),
            "access": tenant.get("access"),
            "isolated": True
        },
        "gateway_controls": {
            "payload_sanitized": True,
            "schema_validated": True,
            "tenant_isolation_checked": True,
            "vault_record_ready": True,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        },
        "core_os_commit": core_os_commit,
        "estimator_result": {
            "baseCost": round(base_cost, 2),
            "adjustedBudget": round(adjusted_budget, 2),
            "contingencyAmount": round(contingency_amount, 2),
            "executionBudget": round(execution_budget, 2),
            "projectScope": project_scope,
            "materialProfile": material_profile
        },
        "execution_blueprint": {
            "operations": operations_blueprint,
            "distribution": distribution_blueprint,
            "finance": finance_blueprint,
            "commerce": commerce_blueprint,
            "vaultRecord": vault_record
        },
        "activity_events": activity_events,
        "review_note": "Execution blueprint is internal QA output. Review before customer-facing use or invoice generation."
    }), 200




# ============================================================
# ASTRAA CORE OS — Unified Business Operating System Routes
# Purpose:
#   Local prototype for shared session, common data model,
#   activity stream, Vault records, event automation, and search.
# ============================================================

# ASTRAA_CORE_OS_PERSISTENCE_V1
ASTRAA_CORE_STORE_PATH = os.path.join("astraa_data", "astraa_core_os_store.json")
# ASTRAA_CORE_OS_RAW_FUNCTION_RESTORE_V1

def astraa_core_default_store():
    return {
        "tenants": {},
        "entities": [],
        "activity": [],
        "events": [],
        "vaultRecords": []
    }

def astraa_core_load_store():
    os.makedirs("astraa_data", exist_ok=True)

    if not os.path.exists(ASTRAA_CORE_STORE_PATH):
        return astraa_core_default_store()

    try:
        with open(ASTRAA_CORE_STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return astraa_core_default_store()

        data.setdefault("tenants", {})
        data.setdefault("entities", [])
        data.setdefault("activity", [])
        data.setdefault("events", [])
        data.setdefault("vaultRecords", [])
        return data

    except Exception:
        return astraa_core_default_store()

def astraa_core_save_store():
    os.makedirs("astraa_data", exist_ok=True)

    payload = {
        "tenants": ASTRAA_CORE_TENANTS,
        "entities": ASTRAA_CORE_ENTITIES,
        "activity": ASTRAA_CORE_ACTIVITY,
        "events": ASTRAA_CORE_EVENTS,
        "vaultRecords": ASTRAA_CORE_VAULT_RECORDS,
        "savedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

    tmp_path = ASTRAA_CORE_STORE_PATH + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    os.replace(tmp_path, ASTRAA_CORE_STORE_PATH)


# ASTRAA_CORE_OS_UPSERT_V1

# ASTRAA_CORE_OS_STORAGE_ABSTRACTION_V1
# ASTRAA_CORE_OS_STORAGE_RECURSION_FIX_V1
# ASTRAA_CORE_OS_STORAGE_STARTUP_ORDER_FIX_V1
def astraa_storage_load_core_store():
    """
    Storage abstraction wrapper for Astraa Core OS store.

    Current backend:
    - JSON file: astraa_data/astraa_core_os_store.json

    Future backend:
    - managed DB tables for entities, activity, events, and vault records.
    """
    if os.getenv("ASTRAA_STORAGE_BACKEND", "json").strip().lower() in ["", "json", "local_json"]:
        return astraa_core_load_store()

    raise RuntimeError("Unsupported ASTRAA_STORAGE_BACKEND for Core OS store. Only json is active.")


def astraa_storage_save_core_store():
    """
    Storage abstraction wrapper for Astraa Core OS store.

    Current backend:
    - delegates to astraa_storage_save_core_store()

    Future backend:
    - managed DB writes for entities, activity, events, and vault records.
    """
    if os.getenv("ASTRAA_STORAGE_BACKEND", "json").strip().lower() in ["", "json", "local_json"]:
        return astraa_core_save_store()

    raise RuntimeError("Unsupported ASTRAA_STORAGE_BACKEND for Core OS store. Only json is active.")


def astraa_core_upsert_entity(entity):
    """
    Upsert entity by tenantId + projectId + entityType.
    This prevents duplicate project records during repeated QA runs.
    """
    tenant_id = entity.get("tenantId")
    project_id = entity.get("projectId")
    entity_type = entity.get("entityType")

    for idx, existing in enumerate(ASTRAA_CORE_ENTITIES):
        if (
            existing.get("tenantId") == tenant_id
            and existing.get("projectId") == project_id
            and existing.get("entityType") == entity_type
        ):
            merged = dict(existing)
            merged.update(entity)
            merged["updatedAt"] = astraa_core_now()
            ASTRAA_CORE_ENTITIES[idx] = merged
            astraa_storage_save_core_store()
            return merged, "updated"

    ASTRAA_CORE_ENTITIES.append(entity)
    astraa_storage_save_core_store()
    return entity, "created"


def astraa_core_upsert_vault_record(record):
    """
    Upsert Vault record by tenantId + projectId + estimateId + recordType.
    This prevents duplicate estimator blueprint Vault records during repeated QA runs.
    """
    tenant_id = record.get("tenantId")
    project_id = record.get("projectId")
    estimate_id = record.get("estimateId")
    record_type = record.get("recordType")

    for idx, existing in enumerate(ASTRAA_CORE_VAULT_RECORDS):
        if (
            existing.get("tenantId") == tenant_id
            and existing.get("projectId") == project_id
            and existing.get("estimateId") == estimate_id
            and existing.get("recordType") == record_type
        ):
            merged = dict(existing)
            merged.update(record)
            merged.setdefault("audit", {})
            merged["audit"]["updatedAt"] = astraa_core_now()
            ASTRAA_CORE_VAULT_RECORDS[idx] = merged
            astraa_storage_save_core_store()
            return merged, "updated"

    ASTRAA_CORE_VAULT_RECORDS.append(record)
    astraa_storage_save_core_store()
    return record, "created"


# ASTRAA_CORE_OS_STORAGE_ADOPTION_V1
ASTRAA_CORE_STORE = astraa_storage_load_core_store()
ASTRAA_CORE_TENANTS = ASTRAA_CORE_STORE.get("tenants", {})
ASTRAA_CORE_ENTITIES = ASTRAA_CORE_STORE.get("entities", [])
ASTRAA_CORE_ACTIVITY = ASTRAA_CORE_STORE.get("activity", [])
ASTRAA_CORE_EVENTS = ASTRAA_CORE_STORE.get("events", [])
ASTRAA_CORE_VAULT_RECORDS = ASTRAA_CORE_STORE.get("vaultRecords", [])

ASTRAA_CORE_ENABLED_TOOLS = [
    "estimator",
    "expense",
    "finance",
    "operations",
    "commerce",
    "data",
    "inference",
    "distribution",
    "vault",
]

ASTRAA_CORE_ENTITY_TYPES = {
    "tenant",
    "organization",
    "contact",
    "project",
    "asset",
    "location",
    "estimate",
    "task",
    "route",
    "expense",
    "invoice",
    "vault_record",
}

def astraa_core_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def astraa_core_id(prefix):
    return prefix + "-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")

def astraa_core_validate_tenant_context(payload):
    tenant = payload.get("tenant_context", {})
    errors = []

    if tenant.get("test_email") != ASTRAA_ALLOWED_TEST_EMAIL:
        errors.append("Invalid test tenant email.")

    if tenant.get("plan") not in ["Trial", "Basic", "Professional", "Custom"]:
        errors.append("Invalid or missing plan.")

    if tenant.get("access") != "Full internal test mode":
        errors.append("Invalid Workspace test access.")

    return errors

def astraa_core_write_activity(event_type, tenant_id, project_id, tool, summary, related=None):
    record = {
        "activityId": astraa_core_id("ACT"),
        "eventType": event_type,
        "tenantId": tenant_id,
        "projectId": project_id,
        "tool": tool,
        "summary": summary,
        "source": "Astraa Gateway",
        "related": related or {},
        "timestamp": astraa_core_now()
    }
    ASTRAA_CORE_ACTIVITY.append(record)
    astraa_storage_save_core_store()
    return record

@app.post("/api/astraa/core/session")
def astraa_core_session():
    raw = request.get_json(silent=True)
    if raw is None:
        return jsonify({"status": "rejected", "gateway": "Astraa Gateway", "errors": ["Invalid or missing JSON payload."]}), 400

    payload = astraa_sanitize(raw)
    errors = astraa_core_validate_tenant_context(payload)
    if errors:
        return jsonify({"status": "rejected", "gateway": "Astraa Gateway", "errors": errors}), 400

    tenant = payload.get("tenant_context", {})
    tenant_id = payload.get("tenantId") or payload.get("tenant_id") or "ASTRAA-QA-TENANT"
    sector = payload.get("sector") or "contractor"

    session = {
        "tenantId": tenant_id,
        "tenantName": payload.get("tenantName") or "Astraa Internal QA",
        "plan": tenant.get("plan"),
        "access": tenant.get("access"),
        "sector": sector,
        "enabledTools": ASTRAA_CORE_ENABLED_TOOLS,
        "sessionMode": "core_os_local_qa",
        "issuedAt": astraa_core_now()
    }

    ASTRAA_CORE_TENANTS[tenant_id] = session
    astraa_storage_save_core_store()

    activity = astraa_core_write_activity(
        "EVENT_CORE_SESSION_VALIDATED",
        tenant_id,
        payload.get("projectId") or "",
        "core",
        "Core OS session validated.",
        {"enabledTools": ASTRAA_CORE_ENABLED_TOOLS}
    )

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "session": session,
        "activity": activity
    }), 200

@app.post("/api/astraa/core/entity")
def astraa_core_entity():
    raw = request.get_json(silent=True)
    if raw is None:
        return jsonify({"status": "rejected", "gateway": "Astraa Gateway", "errors": ["Invalid or missing JSON payload."]}), 400

    payload = astraa_sanitize(raw)
    entity_type = payload.get("entityType")
    tenant_id = payload.get("tenantId") or "ASTRAA-QA-TENANT"
    project_id = payload.get("projectId") or ""

    if entity_type not in ASTRAA_CORE_ENTITY_TYPES:
        return jsonify({
            "status": "rejected",
            "gateway": "Astraa Gateway",
            "errors": [f"Unsupported entityType: {entity_type}"]
        }), 400

    entity = {
        "entityId": payload.get("entityId") or astraa_core_id(entity_type.upper()),
        "entityType": entity_type,
        "tenantId": tenant_id,
        "projectId": project_id,
        "name": payload.get("name") or "",
        "sector": payload.get("sector") or "",
        "location": payload.get("location") or "",
        "data": payload.get("data") or {},
        "createdAt": astraa_core_now(),
        "source": "Astraa Gateway"
    }

    entity, entity_action = astraa_core_upsert_entity(entity)

    activity = astraa_core_write_activity(
        "EVENT_CORE_ENTITY_" + entity_action.upper(),
        tenant_id,
        project_id,
        "core",
        f"{entity_action.title()} {entity_type} entity: {entity.get('name') or entity.get('entityId')}",
        {"entityId": entity["entityId"], "entityType": entity_type, "action": entity_action}
    )

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "entityAction": entity_action,
        "entity": entity,
        "activity": activity
    }), 200

@app.post("/api/astraa/core/activity")
def astraa_core_activity_post():
    raw = request.get_json(silent=True)
    if raw is None:
        return jsonify({"status": "rejected", "gateway": "Astraa Gateway", "errors": ["Invalid or missing JSON payload."]}), 400

    payload = astraa_sanitize(raw)
    record = astraa_core_write_activity(
        payload.get("eventType") or "EVENT_CORE_ACTIVITY",
        payload.get("tenantId") or "ASTRAA-QA-TENANT",
        payload.get("projectId") or "",
        payload.get("tool") or "core",
        payload.get("summary") or "Activity event recorded.",
        payload.get("related") or {}
    )

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "activity": record
    }), 200

@app.get("/api/astraa/core/activity")
def astraa_core_activity_get():
    tenant_id = request.args.get("tenantId")
    project_id = request.args.get("projectId")

    results = ASTRAA_CORE_ACTIVITY

    if tenant_id:
        results = [r for r in results if r.get("tenantId") == tenant_id]

    if project_id:
        results = [r for r in results if r.get("projectId") == project_id]

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "count": len(results),
        "activity": results[-100:]
    }), 200

@app.post("/api/astraa/core/vault-record")
def astraa_core_vault_record():
    raw = request.get_json(silent=True)
    if raw is None:
        return jsonify({"status": "rejected", "gateway": "Astraa Gateway", "errors": ["Invalid or missing JSON payload."]}), 400

    payload = astraa_sanitize(raw)
    tenant_id = payload.get("tenantId") or "ASTRAA-QA-TENANT"
    project_id = payload.get("projectId") or ""

    record = {
        "vaultRecordId": payload.get("vaultRecordId") or astraa_core_id("VAULT"),
        "recordType": payload.get("recordType") or "CORE_OS_RECORD",
        "tenantId": tenant_id,
        "projectId": project_id,
        "sourceTool": payload.get("sourceTool") or "Astraa Core",
        "sourceGateway": "Astraa Gateway",
        "visibility": payload.get("visibility") or "tenant_private",
        "zeroKnowledgeReady": bool(payload.get("zeroKnowledgeReady", True)),
        "linkedPayloads": payload.get("linkedPayloads") or {},
        "storedObjects": payload.get("storedObjects") or [],
        "data": payload.get("data") or {},
        "audit": {
            "payloadSanitized": True,
            "schemaValidated": True,
            "tenantIsolationChecked": True,
            "createdAt": astraa_core_now()
        }
    }

    record, vault_action = astraa_core_upsert_vault_record(record)

    activity = astraa_core_write_activity(
        "EVENT_CORE_VAULT_RECORD_" + vault_action.upper(),
        tenant_id,
        project_id,
        "vault",
        f"Vault record {vault_action}: {record['recordType']}",
        {"vaultRecordId": record["vaultRecordId"], "action": vault_action}
    )

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "vaultRecordAction": vault_action,
        "vaultRecord": record,
        "activity": activity
    }), 200

@app.post("/api/astraa/core/event")
def astraa_core_event():
    raw = request.get_json(silent=True)
    if raw is None:
        return jsonify({"status": "rejected", "gateway": "Astraa Gateway", "errors": ["Invalid or missing JSON payload."]}), 400

    payload = astraa_sanitize(raw)

    tenant_id = payload.get("tenantId") or "ASTRAA-QA-TENANT"
    project_id = payload.get("projectId") or ""
    event_type = payload.get("eventType") or "EVENT_CORE_GENERIC"
    tool = payload.get("tool") or "core"

    event = {
        "eventId": payload.get("eventId") or astraa_core_id("EVT"),
        "eventType": event_type,
        "tenantId": tenant_id,
        "projectId": project_id,
        "tool": tool,
        "payload": payload.get("payload") or {},
        "timestamp": astraa_core_now(),
        "source": "Astraa Gateway"
    }

    ASTRAA_CORE_EVENTS.append(event)
    astraa_storage_save_core_store()

    triggered = []

    if event_type == "EVENT_PROJECT_MILESTONE_COMPLETE":
        triggered = [
            "finance_progress_invoice_draft_ready",
            "vault_milestone_record_ready",
            "activity_stream_updated"
        ]
    elif event_type == "EVENT_ESTIMATE_BLUEPRINT_GENERATED":
        triggered = [
            "operations_blueprint_ready",
            "distribution_blueprint_ready",
            "finance_blueprint_ready",
            "vault_record_ready"
        ]
    else:
        triggered = ["activity_stream_updated"]

    activity = astraa_core_write_activity(
        event_type,
        tenant_id,
        project_id,
        tool,
        payload.get("summary") or f"Event published: {event_type}",
        {"eventId": event["eventId"], "triggeredActions": triggered}
    )

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "eventAccepted": True,
        "event": event,
        "triggeredActions": triggered,
        "activity": activity
    }), 200

@app.post("/api/astraa/core/search")
def astraa_core_search():
    raw = request.get_json(silent=True)
    if raw is None:
        return jsonify({"status": "rejected", "gateway": "Astraa Gateway", "errors": ["Invalid or missing JSON payload."]}), 400

    payload = astraa_sanitize(raw)
    tenant_id = payload.get("tenantId") or "ASTRAA-QA-TENANT"
    query = str(payload.get("query") or "").lower().strip()

    def contains_query(obj):
        return query in json.dumps(obj, default=str).lower()

    if not query:
        return jsonify({
            "status": "rejected",
            "gateway": "Astraa Gateway",
            "errors": ["Search query is required."]
        }), 400

    entities = [x for x in ASTRAA_CORE_ENTITIES if x.get("tenantId") == tenant_id and contains_query(x)]
    activity = [x for x in ASTRAA_CORE_ACTIVITY if x.get("tenantId") == tenant_id and contains_query(x)]
    events = [x for x in ASTRAA_CORE_EVENTS if x.get("tenantId") == tenant_id and contains_query(x)]
    vault_records = [x for x in ASTRAA_CORE_VAULT_RECORDS if x.get("tenantId") == tenant_id and contains_query(x)]

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "query": query,
        "tenantId": tenant_id,
        "results": {
            "entities": entities[-25:],
            "activity": activity[-25:],
            "events": events[-25:],
            "vaultRecords": vault_records[-25:]
        }
    }), 200




# ============================================================
# ASTRAA ESTIMATOR USAGE ENFORCEMENT — LOCAL/STAGING V1
# Purpose:
#   Backend-side usage enforcement for Astraa Estimator.
#   This is a staging-prep route and does not replace final
#   payment verification / Moneris subscription enforcement yet.
# ============================================================

ASTRAA_USAGE_DB_PATH = os.path.join("astraa_data", "astraa_usage_db.json")

ESTIMATOR_PLAN_LIMITS = {
    "Trial": {
        "estimate_limit": 15,
        "daily_limit": 1,
        "requires_payment": False,
        "period_type": "trial_15_days"
    },
    "Basic": {
        "estimate_limit": 30,
        "daily_limit": None,
        "requires_payment": True,
        "period_type": "monthly"
    },
    "Professional": {
        "estimate_limit": 120,
        "daily_limit": None,
        "requires_payment": True,
        "period_type": "monthly"
    }
}


def astraa_today_date():
    return datetime.now(timezone.utc).date()


def astraa_today_key():
    return astraa_today_date().isoformat()


def astraa_month_key():
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m")


def astraa_month_start():
    now = datetime.now(timezone.utc)
    return now.replace(day=1).date().isoformat()


def astraa_month_end():
    now = datetime.now(timezone.utc)

    if now.month == 12:
        next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month + 1, day=1)

    return (next_month.date() - timedelta(days=1)).isoformat()


def astraa_load_usage_db():
    os.makedirs("astraa_data", exist_ok=True)

    if not os.path.exists(ASTRAA_USAGE_DB_PATH):
        return {}

    try:
        with open(ASTRAA_USAGE_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}

    except Exception:
        return {}


def astraa_save_usage_db(db):
    os.makedirs("astraa_data", exist_ok=True)

    tmp_path = ASTRAA_USAGE_DB_PATH + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, sort_keys=True)

    os.replace(tmp_path, ASTRAA_USAGE_DB_PATH)


def astraa_default_usage_record(account_email, plan):
    plan_rules = ESTIMATOR_PLAN_LIMITS.get(plan, ESTIMATOR_PLAN_LIMITS["Trial"])

    return {
        "account_id": account_email,
        "primary_email": account_email,
        "business_name": "",
        "selected_tool": "Astraa Estimator",
        "selected_plan": plan,
        "payment_status": "trial" if plan == "Trial" else "inactive",
        "subscription_status": "trial" if plan == "Trial" else "inactive",

        "billing_period_key": astraa_month_key(),
        "billing_period_start": astraa_month_start(),
        "billing_period_end": astraa_month_end(),

        "estimate_limit": plan_rules["estimate_limit"],
        "estimate_used": 0,

        "trial_start_date": astraa_today_key() if plan == "Trial" else None,
        "last_trial_estimate_date": None,
        "daily_limit": plan_rules["daily_limit"],

        "extra_estimate_credits_total": 0,
        "extra_estimate_credits_used": 0,

        "custom_limit_config": None,
        "saved_estimates": [],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


def astraa_get_usage_record(account_email, requested_plan="Trial"):
    db = astraa_storage_load_usage_db()

    account_email = str(account_email or "").strip().lower()
    if not account_email:
        account_email = "anonymous@astraa.local"

    if account_email not in db:
        db[account_email] = astraa_default_usage_record(account_email, requested_plan)
        astraa_storage_save_usage_db(db)

    return db, db[account_email]


def astraa_reset_monthly_period_if_needed(record):
    current_key = astraa_month_key()

    if record.get("billing_period_key") != current_key:
        record["billing_period_key"] = current_key
        record["billing_period_start"] = astraa_month_start()
        record["billing_period_end"] = astraa_month_end()
        record["estimate_used"] = 0
        record["extra_estimate_credits_used"] = 0
        record["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return record


def astraa_trial_expired(record):
    trial_start = record.get("trial_start_date")

    if not trial_start:
        return False

    try:
        start_date = date.fromisoformat(trial_start)
        days_used = (astraa_today_date() - start_date).days
        return days_used >= 15
    except Exception:
        return False


def astraa_effective_estimate_allowance(record):
    base_limit = int(record.get("estimate_limit") or 0)
    extra_total = int(record.get("extra_estimate_credits_total") or 0)
    extra_used = int(record.get("extra_estimate_credits_used") or 0)
    extra_remaining = max(extra_total - extra_used, 0)

    return base_limit + extra_remaining


def astraa_enforce_estimator_usage(record):
    plan = record.get("selected_plan") or "Trial"
    tool = record.get("selected_tool") or "Astraa Estimator"

    if tool != "Astraa Estimator":
        return False, "Selected tool is not Astraa Estimator.", record

    if plan in ["Basic", "Professional"]:
        record = astraa_reset_monthly_period_if_needed(record)

    if plan == "Trial":
        if astraa_trial_expired(record):
            return False, "Trial period expired.", record

        if int(record.get("estimate_used") or 0) >= 15:
            return False, "Trial estimate limit reached.", record

        if record.get("last_trial_estimate_date") == astraa_today_key():
            return False, "Daily trial estimate limit reached.", record

        return True, "Allowed", record

    if plan in ["Basic", "Professional"]:
        if record.get("payment_status") != "active" or record.get("subscription_status") != "active":
            return False, "Payment/subscription is not active.", record

        allowance = astraa_effective_estimate_allowance(record)
        used = int(record.get("estimate_used") or 0)

        if used >= allowance:
            return False, "Monthly estimate limit reached. Add an estimate pack or upgrade.", record

        return True, "Allowed", record

    if plan in ["Custom", "Franchise", "Enterprise"]:
        if record.get("payment_status") != "active" or record.get("subscription_status") != "active":
            return False, "Custom package payment/subscription is not active.", record

        custom_config = record.get("custom_limit_config") or {}
        custom_limit = int(custom_config.get("estimate_limit") or record.get("estimate_limit") or 0)

        if custom_limit and int(record.get("estimate_used") or 0) >= custom_limit:
            return False, "Custom package estimate limit reached.", record

        return True, "Allowed", record

    return False, "Unsupported Estimator plan.", record


def astraa_record_successful_estimator_usage(db, record, estimate_summary):
    plan = record.get("selected_plan") or "Trial"

    record["estimate_used"] = int(record.get("estimate_used") or 0) + 1

    if plan == "Trial":
        record["last_trial_estimate_date"] = astraa_today_key()

    base_limit = int(record.get("estimate_limit") or 0)

    # If user has exceeded base plan limit because of extra packs,
    # count the overflow against extra_estimate_credits_used.
    if record["estimate_used"] > base_limit:
        overflow = record["estimate_used"] - base_limit
        record["extra_estimate_credits_used"] = min(
            overflow,
            int(record.get("extra_estimate_credits_total") or 0)
        )

    record.setdefault("saved_estimates", [])
    record["saved_estimates"].append({
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "backend_estimator_usage_enforcement",
        "estimate": estimate_summary
    })

    record["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    db[record["account_id"]] = record
    astraa_storage_save_usage_db(db)

    return record


# ============================================================
# ASTRAA ESTIMATOR ENFORCED RUN ROUTE — LOCAL/STAGING V1
# ============================================================

@app.post("/api/astraa/estimator/enforced-run")
def astraa_estimator_enforced_run():
    raw_payload = request.get_json(silent=True)


    # ASTRAA_ESTIMATOR_ACCOUNT_AUTHORITY_GUARD_V1
    try:
        estimator_payload_for_authority = raw_payload if "raw_payload" in locals() else payload if "payload" in locals() else data if "data" in locals() else {}
    except Exception:
        estimator_payload_for_authority = {}

    estimator_account_authority = astraa_resolve_account_authority(estimator_payload_for_authority, request)

    if not estimator_account_authority.get("allowed"):
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "reason": estimator_account_authority.get("reason"),
            "identity_source": estimator_account_authority.get("identity_source"),
            "review_note": "Estimator request blocked by account authority guard."
        }), 403

    # ASTRAA_ESTIMATOR_ACCOUNT_AUTHORITY_OVERRIDE_V1
    # Once account authority is resolved, force downstream Estimator logic to use
    # the backend-authorized account identity instead of any frontend-submitted email.
    try:
        authoritative_account_email = estimator_account_authority.get("account_email")
        authoritative_selected_plan = estimator_account_authority.get("selected_plan")

        if authoritative_account_email:
            if "raw_payload" in locals() and isinstance(raw_payload, dict):
                raw_payload.setdefault("inputs", {})
                raw_payload["inputs"]["account_email"] = authoritative_account_email
                raw_payload["account_email"] = authoritative_account_email

            if "payload" in locals() and isinstance(payload, dict):
                payload.setdefault("inputs", {})
                payload["inputs"]["account_email"] = authoritative_account_email
                payload["account_email"] = authoritative_account_email

            if "data" in locals() and isinstance(data, dict):
                data.setdefault("inputs", {})
                data["inputs"]["account_email"] = authoritative_account_email
                data["account_email"] = authoritative_account_email

        if authoritative_selected_plan:
            if "raw_payload" in locals() and isinstance(raw_payload, dict):
                raw_payload.setdefault("inputs", {})
                raw_payload["inputs"]["selected_plan"] = authoritative_selected_plan
                raw_payload["selected_plan"] = authoritative_selected_plan

            if "payload" in locals() and isinstance(payload, dict):
                payload.setdefault("inputs", {})
                payload["inputs"]["selected_plan"] = authoritative_selected_plan
                payload["selected_plan"] = authoritative_selected_plan

            if "data" in locals() and isinstance(data, dict):
                data.setdefault("inputs", {})
                data["inputs"]["selected_plan"] = authoritative_selected_plan
                data["selected_plan"] = authoritative_selected_plan

    except Exception:
        pass

    # ASTRAA_ESTIMATOR_SCHEMA_VALIDATION_ROUTE_GUARD_V1
    try:
        estimator_inputs_for_validation = {}

        if "raw_payload" in locals() and isinstance(raw_payload, dict):
            estimator_inputs_for_validation = raw_payload.get("inputs") or {}
        elif "payload" in locals() and isinstance(payload, dict):
            estimator_inputs_for_validation = payload.get("inputs") or {}
        elif "data" in locals() and isinstance(data, dict):
            estimator_inputs_for_validation = data.get("inputs") or {}

        valid_estimator_inputs, estimator_input_errors, clean_estimator_inputs = astraa_validate_estimator_inputs(
            estimator_inputs_for_validation
        )

        if not valid_estimator_inputs:
            return jsonify({
                "status": "blocked",
                "gateway": "Astraa Gateway",
                "reason": "Invalid Estimator input.",
                "errors": estimator_input_errors,
                "review_note": "Estimator request blocked by schema validation."
            }), 400

        for target_name in ["raw_payload", "payload", "data"]:
            target = locals().get(target_name)
            if isinstance(target, dict):
                target.setdefault("inputs", {})
                target["inputs"].update(clean_estimator_inputs)

    except Exception as validation_error:
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "reason": "Estimator input validation failed.",
            "errors": [str(validation_error)],
            "review_note": "Estimator request blocked by schema validation."
        }), 400


    if raw_payload is None:
        return jsonify({
            "status": "rejected",
            "gateway": "Astraa Gateway",
            "errors": ["Invalid or missing JSON payload."]
        }), 400

    payload = astraa_sanitize(raw_payload)
    inputs = payload.get("inputs", {})

    account_email = (
        inputs.get("account_email")
        or payload.get("account_email")
        or payload.get("tenant_context", {}).get("test_email")
    )

    requested_plan = (
        inputs.get("selected_plan")
        or payload.get("selected_plan")
        or payload.get("tenant_context", {}).get("plan")
        or "Trial"
    )

    db, record = astraa_get_usage_record(account_email, requested_plan)
    allowed, reason, record = astraa_enforce_estimator_usage(record)

    if not allowed:
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "reason": reason,
            "usage": {
                "plan": record.get("selected_plan"),
                "estimate_used": record.get("estimate_used"),
                "estimate_limit": record.get("estimate_limit"),
                "extra_estimate_credits_total": record.get("extra_estimate_credits_total"),
                "extra_estimate_credits_used": record.get("extra_estimate_credits_used"),
                "billing_period_key": record.get("billing_period_key"),
                "last_trial_estimate_date": record.get("last_trial_estimate_date")
            }
        }), 403

    base_cost = astraa_safe_float(inputs.get("base_cost"))
    complexity_factor = astraa_safe_float(inputs.get("complexity_factor"), 1)
    material_multiplier = astraa_safe_float(inputs.get("material_multiplier"), 1)
    labor_multiplier = astraa_safe_float(inputs.get("labor_multiplier"), 1)
    location_multiplier = astraa_safe_float(inputs.get("location_multiplier"), 1)

    estimate_total = (
        base_cost
        * complexity_factor
        * material_multiplier
        * labor_multiplier
        * location_multiplier
    )

    estimate_summary = {
        "base_cost": round(base_cost, 2),
        "complexity_factor": complexity_factor,
        "material_multiplier": material_multiplier,
        "labor_multiplier": labor_multiplier,
        "location_multiplier": location_multiplier,
        "estimated_total": round(estimate_total, 2)
    }

    record = astraa_record_successful_estimator_usage(db, record, estimate_summary)

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "tool": "Astraa Estimator",
        "result": estimate_summary,
        "usage": {
            "plan": record.get("selected_plan"),
            "estimate_used": record.get("estimate_used"),
            "estimate_limit": record.get("estimate_limit"),
            "extra_estimate_credits_total": record.get("extra_estimate_credits_total"),
            "extra_estimate_credits_used": record.get("extra_estimate_credits_used"),
            "billing_period_key": record.get("billing_period_key"),
            "billing_period_start": record.get("billing_period_start"),
            "billing_period_end": record.get("billing_period_end"),
            "last_trial_estimate_date": record.get("last_trial_estimate_date")
        },
        "review_note": "Backend usage enforcement test route. Production payment verification still required before public launch."
    }), 200




# ============================================================
# ASTRAA PAYMENT VERIFICATION — MONERIS RECEIPT ROUTE V1
# Purpose:
#   Server-side payment verification before activating plans
#   or applying estimate packs.
#
# Notes:
#   - Local QA simulation is supported for internal testing.
#   - Real Moneris verification requires backend env variables.
#   - Do not expose store_id/api_token/checkout_id in frontend JS.
# ============================================================

ASTRAA_PAYMENT_DB_PATH = os.path.join("astraa_data", "astraa_payment_db.json")

MONERIS_RECEIPT_URLS = {
    "qa": "https://gatewayt.moneris.com/chkt/request/request.php",
    "prod": "https://gateway.moneris.com/chkt/request/request.php"
}


def astraa_payment_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def astraa_load_payment_db():
    os.makedirs("astraa_data", exist_ok=True)

    if not os.path.exists(ASTRAA_PAYMENT_DB_PATH):
        return []

    try:
        with open(ASTRAA_PAYMENT_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, list) else []

    except Exception:
        return []


def astraa_save_payment_db(records):
    os.makedirs("astraa_data", exist_ok=True)

    tmp_path = ASTRAA_PAYMENT_DB_PATH + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, sort_keys=True)

    os.replace(tmp_path, ASTRAA_PAYMENT_DB_PATH)




# ASTRAA_STORAGE_ABSTRACTION_V1
def astraa_storage_backend():
    """
    Storage backend selector.

    Current public-launch hardening state:
    - json is the only active backend.
    - db is reserved for future managed database migration.
    """
    return os.getenv("ASTRAA_STORAGE_BACKEND", "json").strip().lower()


def astraa_storage_backend_is_json():
    return astraa_storage_backend() in ["", "json", "local_json"]


def astraa_storage_load_usage_db():
    """
    Storage abstraction wrapper for usage records.
    Currently delegates to the active JSON implementation.
    """
    if astraa_storage_backend_is_json():
        return astraa_load_usage_db()

    raise RuntimeError("Unsupported ASTRAA_STORAGE_BACKEND for usage DB. Only json is active.")


def astraa_storage_save_usage_db(db):
    """
    Storage abstraction wrapper for usage records.
    Currently delegates to the active JSON implementation.
    """
    if astraa_storage_backend_is_json():
        return astraa_save_usage_db(db)

    raise RuntimeError("Unsupported ASTRAA_STORAGE_BACKEND for usage DB. Only json is active.")


def astraa_storage_load_payment_db():
    """
    Storage abstraction wrapper for payment records.
    Currently delegates to the active JSON implementation.
    """
    if astraa_storage_backend_is_json():
        return astraa_load_payment_db()

    raise RuntimeError("Unsupported ASTRAA_STORAGE_BACKEND for payment DB. Only json is active.")


def astraa_storage_save_payment_db(records):
    """
    Storage abstraction wrapper for payment records.
    Currently delegates to the active JSON implementation.
    """
    if astraa_storage_backend_is_json():
        return astraa_save_payment_db(records)

    raise RuntimeError("Unsupported ASTRAA_STORAGE_BACKEND for payment DB. Only json is active.")


# ASTRAA_MANAGED_DB_ADAPTER_SKELETON_V1_START
def astraa_storage_backend():
    """
    Return configured storage backend.

    Safe default:
    - json

    Future backend:
    - managed_db

    This helper does not connect to a database.
    """
    return os.getenv("ASTRAA_STORAGE_BACKEND", "json").strip().lower()


def astraa_managed_db_adapter_selected():
    """
    Return whether managed DB backend is explicitly selected.

    Selecting managed_db does not mean it is implemented or safe to use yet.
    """
    return astraa_storage_backend() in {"managed_db", "postgres", "postgresql"}


def astraa_managed_db_required_env():
    """
    Required environment names for future managed DB adapter use.

    Presence checks must never print secret values.
    """
    return [
        "ASTRAA_STORAGE_BACKEND",
        "ASTRAA_MANAGED_DB_ENGINE",
        "ASTRAA_MANAGED_DB_URL",
    ]


def astraa_managed_db_config_status():
    """
    Return managed DB configuration status without exposing secret values.

    This is a safe presence/shape check only.
    It does not connect to managed DB.
    It does not create tables.
    It does not migrate data.
    """
    backend = astraa_storage_backend()
    engine = os.getenv("ASTRAA_MANAGED_DB_ENGINE", "").strip().lower()
    has_url = bool(os.getenv("ASTRAA_MANAGED_DB_URL", "").strip())

    missing = []

    if backend in {"managed_db", "postgres", "postgresql"}:
        if not engine:
            missing.append("ASTRAA_MANAGED_DB_ENGINE")
        if engine in {"postgres", "postgresql", "managed_db"} and not has_url:
            missing.append("ASTRAA_MANAGED_DB_URL")

    return {
        "storage_backend": backend,
        "managed_db_selected": backend in {"managed_db", "postgres", "postgresql"},
        "engine": engine or None,
        "configured": not missing if backend in {"managed_db", "postgres", "postgresql"} else False,
        "missing": missing,
        "secret_values_exposed": False,
    }


def astraa_managed_db_adapter_blocked(operation, store_name):
    """
    Return a standard fail-closed managed DB adapter response.

    Future adapter implementation should replace this only after:
    - managed staging DB proof exists
    - schema/index proof exists
    - import/reconcile proof exists
    - production secrets are secure
    """
    status = astraa_managed_db_config_status()

    return {
        "status": "blocked",
        "storage_backend": status.get("storage_backend"),
        "managed_db_selected": status.get("managed_db_selected"),
        "engine": status.get("engine"),
        "configured": status.get("configured"),
        "missing": status.get("missing"),
        "operation": operation,
        "store_name": store_name,
        "reason": (
            "Managed DB adapter skeleton is present but real managed DB storage "
            "operations are not implemented yet. JSON/local storage remains the safe default."
        ),
    }


def astraa_managed_db_load_store_stub(store_name):
    """
    Fail-closed placeholder for future managed DB load operations.

    Does not connect to a database.
    """
    raise RuntimeError(str(astraa_managed_db_adapter_blocked("load", store_name)))


def astraa_managed_db_save_store_stub(store_name, data):
    """
    Fail-closed placeholder for future managed DB save operations.

    Does not connect to a database.
    """
    raise RuntimeError(str(astraa_managed_db_adapter_blocked("save", store_name)))
# ASTRAA_MANAGED_DB_ADAPTER_SKELETON_V1_END

def astraa_storage_load_sessions_db():
    """
    Storage abstraction wrapper for session records.
    Currently delegates to the active JSON implementation.
    """
    if astraa_storage_backend_is_json():
        return astraa_load_sessions_db()

    raise RuntimeError("Unsupported ASTRAA_STORAGE_BACKEND for sessions DB. Only json is active.")


def astraa_storage_save_sessions_db(db):
    """
    Storage abstraction wrapper for session records.
    Currently delegates to the active JSON implementation.
    """
    if astraa_storage_backend_is_json():
        return astraa_save_sessions_db(db)

    raise RuntimeError("Unsupported ASTRAA_STORAGE_BACKEND for sessions DB. Only json is active.")




# ASTRAA_EVENT_LOG_STORAGE_ABSTRACTION_V1
def astraa_storage_event_log_path(log_name):
    """
    Map logical event log names to current JSONL files.

    Current backend:
    - JSONL files remain active.
    - Future backend:
      - these logical names can map to DB event tables.
    """
    name = str(log_name or "").strip().lower()

    mapping = {
        "preloads": PRELOADS_FILE,
        "payments": PAYMENTS_FILE,
        "receipts": RECEIPTS_FILE if "RECEIPTS_FILE" in globals() else "receipts.jsonl",
        "leads": "leads.jsonl",
    }

    if name not in mapping:
        raise ValueError(f"Unsupported Astraa event log name: {log_name}")

    return mapping[name]


def astraa_storage_append_event_log(log_name, record):
    """
    Storage abstraction wrapper for append-only JSONL event logs.

    Current behavior:
    - delegates to append_jsonl(...)
    - does not change event record shape
    - keeps JSONL backend active

    Future behavior:
    - can route to managed DB event tables using log_name.
    """
    if astraa_storage_backend_is_json():
        return append_jsonl(astraa_storage_event_log_path(log_name), record)

    raise RuntimeError("Unsupported ASTRAA_STORAGE_BACKEND for event logs. Only json is active.")


def astraa_payment_record_id(prefix="PAY"):
    return prefix + "-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")








# ASTRAA_ACCOUNT_AUTHORITY_V1
def astraa_public_launch_mode_enabled():
    """
    Public launch mode is intentionally stricter.
    In this mode, payment/usage routes should not trust browser-submitted account_email.
    """
    return (
        os.getenv("ASTRAA_PUBLIC_LAUNCH_MODE", "false")
        .strip()
        .lower()
        in ["1", "true", "yes"]
    )


def astraa_clean_email(value):
    return str(value or "").strip().lower()


def astraa_extract_requested_account_email(payload):
    """
    Controlled-dev extractor.
    This preserves current testing behavior while making the trust boundary explicit.
    """
    if not isinstance(payload, dict):
        return ""

    tenant_context = payload.get("tenant_context") or {}
    inputs = payload.get("inputs") or {}

    return astraa_clean_email(
        payload.get("account_email")
        or payload.get("email")
        or payload.get("customer_email")
        or tenant_context.get("test_email")
        or inputs.get("account_email")
        or inputs.get("email")
    )


def astraa_resolve_account_authority(payload, req=None):
    """
    controlled_dev:
      Allows account_email from request payload for internal/local testing.

    public_launch:
      Requires backend-authenticated account identity.

    Current backend-authenticated bridge:
      Authorization: Bearer <dev-session-token>
    """
    if req is not None:
        session_identity = astraa_resolve_session_identity(req)
        if session_identity:
            return session_identity

    requested_email = astraa_extract_requested_account_email(payload)

    if astraa_public_launch_mode_enabled():
        return {
            "allowed": False,
            "account_email": requested_email,
            "identity_source": "blocked_frontend_submitted_identity",
            "reason": (
                "Public launch mode is enabled. Backend-authenticated account identity "
                "is required before accepting account-scoped payment or Estimator actions."
            )
        }

    return {
        "allowed": bool(requested_email),
        "account_email": requested_email,
        "identity_source": "controlled_dev_payload",
        "reason": "Controlled-dev mode allowed request payload account identity."
    }


# ASTRAA_USAGE_NORMALIZATION_V1
def astraa_int_or_zero(value):
    try:
        if value is None or value == "":
            return 0
        return int(value)
    except Exception:
        return 0


def astraa_normalize_usage_record(record):
    """
    Normalize usage fields so public API responses do not expose null counters.
    This is safe for local JSON and future DB-backed records.
    """
    if not isinstance(record, dict):
        return record

    record["estimate_used"] = astraa_int_or_zero(record.get("estimate_used"))
    record["estimate_limit"] = astraa_int_or_zero(record.get("estimate_limit"))
    record["extra_estimate_credits_total"] = astraa_int_or_zero(record.get("extra_estimate_credits_total"))
    record["extra_estimate_credits_used"] = astraa_int_or_zero(record.get("extra_estimate_credits_used"))

    return record


# ASTRAA_PAYMENT_IDEMPOTENCY_V1
def astraa_payment_idempotency_key(account_email, purchase_type, ticket):
    raw = "|".join([
        str(account_email or "").strip().lower(),
        str(purchase_type or "").strip(),
        str(ticket or "").strip()
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def astraa_find_verified_payment_by_idempotency(payment_db, idempotency_key):
    for record in payment_db:
        if (
            record.get("idempotency_key") == idempotency_key
            and record.get("verified") is True
            and record.get("receipt_approved") is True
        ):
            return record
    return None


def astraa_usage_summary_for_account(account_email):
    db = astraa_storage_load_usage_db()
    account_email = str(account_email or "").strip().lower()
    record = db.get(account_email)

    if not record:
        return None

    record = astraa_normalize_usage_record(record)

    return {
        "account_id": record.get("account_id"),
        "selected_plan": record.get("selected_plan"),
        "payment_status": record.get("payment_status"),
        "subscription_status": record.get("subscription_status"),
        "estimate_limit": record.get("estimate_limit"),
        "estimate_used": record.get("estimate_used"),
        "extra_estimate_credits_total": record.get("extra_estimate_credits_total"),
        "extra_estimate_credits_used": record.get("extra_estimate_credits_used"),
        "billing_period_key": record.get("billing_period_key")
    }


def astraa_moneris_env():
    return (os.getenv("MONERIS_ENV") or "qa").strip().lower()


def astraa_moneris_simulation_enabled():
    return (os.getenv("ASTRAA_MONERIS_SIMULATION", "true").strip().lower() in ["1", "true", "yes"])




# ASTRAA_MONERIS_PROD_SIMULATION_GUARD_V1
def astraa_moneris_prod_simulation_allowed():
    return (
        os.getenv("ASTRAA_ALLOW_PROD_SIMULATION", "false")
        .strip()
        .lower()
        in ["1", "true", "yes"]
    )


def astraa_moneris_environment_guard():
    """
    Prevent accidental local/simulated payment verification while configured for production.
    This protects against MONERIS_ENV=prod + ASTRAA_MONERIS_SIMULATION=true.
    """
    env = astraa_moneris_env()
    simulation = astraa_moneris_simulation_enabled()

    if env == "prod" and simulation and not astraa_moneris_prod_simulation_allowed():
        return False, (
            "Blocked unsafe payment verification mode: MONERIS_ENV=prod with "
            "ASTRAA_MONERIS_SIMULATION=true. Set MONERIS_ENV=qa for local simulation, "
            "or set ASTRAA_MONERIS_SIMULATION=false for real Moneris production receipt verification. "
            "Only set ASTRAA_ALLOW_PROD_SIMULATION=true for an intentional internal override."
        )

    return True, "Environment guard passed."






# ASTRAA_PAYMENT_SCHEMA_VALIDATION_V1
def astraa_validate_payment_verification_payload(payload):
    """
    Validate payment verification request shape before receipt verification.
    Account identity is resolved separately by account authority.
    """
    if not isinstance(payload, dict):
        return False, ["payload must be an object."], {}

    errors = []
    clean = {}

    selected_tool = str(payload.get("selected_tool") or payload.get("tool") or "Astraa Estimator").strip()
    selected_tool_l = selected_tool.lower()

    allowed_tools = {
        "astraa estimator",
        "estimator"
    }

    if selected_tool_l not in allowed_tools:
        errors.append("selected_tool must be Astraa Estimator for this payment flow.")

    clean["selected_tool"] = "Astraa Estimator"

    selected_plan = str(payload.get("selected_plan") or payload.get("plan") or "").strip()
    selected_plan_l = selected_plan.lower()

    allowed_plans = {
        "trial",
        "basic",
        "professional",
        "custom",
        ""
    }

    if selected_plan_l not in allowed_plans:
        errors.append("selected_plan must be Trial, Basic, Professional, or Custom.")

    clean["selected_plan"] = selected_plan or "Professional"

    purchase_type = str(payload.get("purchase_type") or "").strip().lower()

    allowed_purchase_types = {
        "subscription_trial",
        "subscription_basic",
        "subscription_professional",
        "subscription_custom",
        "estimate_pack",
        "estimate_pack_10",
        "extra_estimate_pack",
        "extra_estimate_pack_10"
    }

    if purchase_type not in allowed_purchase_types:
        errors.append("purchase_type is required and must be a known Astraa purchase type.")

    clean["purchase_type"] = purchase_type

    moneris_ticket = str(
        payload.get("moneris_ticket")
        or payload.get("ticket")
        or payload.get("astraa_moneris_ticket")
        or ""
    ).strip()

    if not moneris_ticket:
        errors.append("moneris_ticket is required.")
    elif len(moneris_ticket) < 12:
        errors.append("moneris_ticket is too short.")
    elif len(moneris_ticket) > 256:
        errors.append("moneris_ticket is too long.")
    elif not re.match(r"^[A-Za-z0-9_\-]+$", moneris_ticket):
        errors.append("moneris_ticket contains invalid characters.")

    clean["moneris_ticket"] = moneris_ticket

    return len(errors) == 0, errors, clean


# ASTRAA_MONERIS_APPROVAL_GUARD_V1
def astraa_iter_nested_values(obj):
    """
    Recursively yields (key, value) pairs from nested dict/list structures.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield str(key), value
            yield from astraa_iter_nested_values(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from astraa_iter_nested_values(item)


def astraa_moneris_receipt_declined(raw):
    """
    Conservative decline detector.
    If any obvious declined/cancelled/not-approved marker exists, block activation.
    """
    declined_words = [
        "declined",
        "decline",
        "not approved",
        "not_approved",
        "cancelled",
        "canceled",
        "failed",
        "failure"
    ]

    approval_keys = {
        "approval_code",
        "auth_code",
        "authorization_code",
        "authorizationcode",
        "authcode"
    }

    for key, value in astraa_iter_nested_values(raw):
        key_l = str(key or "").strip().lower()
        value_s = str(value or "").strip()
        value_l = value_s.lower()

        if any(word in value_l for word in declined_words):
            return True, f"Decline marker found: {key}={value_s}"

        if key_l in approval_keys and value_s in ["", "000000", "0", "00000"]:
            return True, f"Invalid approval/auth code: {key}={value_s}"

    return False, ""


def astraa_moneris_receipt_approved(raw):
    """
    Conservative approval detector.
    We require explicit approval evidence and no decline markers.

    Important:
    response.success=true only means the receipt request succeeded.
    It does not by itself prove the transaction was approved.
    """
    declined, decline_reason = astraa_moneris_receipt_declined(raw)
    if declined:
        return False, decline_reason

    approval_keys = {
        "approval_code",
        "auth_code",
        "authorization_code",
        "authorizationcode",
        "authcode"
    }

    approved_keys = {
        "approved",
        "is_approved",
        "transaction_approved",
        "payment_approved"
    }

    status_keys = {
        "status",
        "transaction_status",
        "payment_status",
        "result",
        "decision"
    }

    for key, value in astraa_iter_nested_values(raw):
        key_l = str(key or "").strip().lower()
        value_s = str(value or "").strip()
        value_l = value_s.lower()

        if key_l in approval_keys and value_s not in ["", "000000", "0", "00000", "none", "null"]:
            return True, f"Approval/auth code found: {key}"

        if key_l in approved_keys and value_l in ["true", "yes", "approved", "approve", "1"]:
            return True, f"Approved flag found: {key}={value_s}"

        if key_l in status_keys and value_l in ["approved", "approve", "completed", "complete", "success", "successful"]:
            return True, f"Approved status found: {key}={value_s}"

    return False, "Receipt request succeeded, but no explicit approval evidence was found."



def astraa_verify_moneris_receipt(ticket):
    """
    Returns:
      {
        "verified": bool,
        "source": "simulation" or "moneris_receipt_request",
        "raw": dict,
        "reason": str
      }

    Local QA simulation:
      Accepts tickets starting with ASTRAA-QA- or QA- only when
      ASTRAA_MONERIS_SIMULATION=true.

    Real Moneris mode:
      Sends receipt request server-to-server using backend env vars.
    """
    ticket = str(ticket or "").strip()

    if not ticket:
        return {
            "verified": False,
            "source": "local_validation",
            "raw": {},
            "reason": "Missing Moneris ticket."
        }

    env_guard_ok, env_guard_reason = astraa_moneris_environment_guard()
    if not env_guard_ok:
        return {
            "verified": False,
            "source": "environment_guard",
            "raw": {
                "environment": astraa_moneris_env(),
                "simulation": astraa_moneris_simulation_enabled()
            },
            "reason": env_guard_reason
        }

    env = astraa_moneris_env()

    # Local/internal QA simulation. This is NOT Moneris behavior.
    # It is only an Astraa test harness so frontend payment flow can be wired safely.
    if astraa_moneris_simulation_enabled():
        if ticket.startswith("ASTRAA-QA-") or ticket.startswith("QA-"):
            return {
                "verified": True,
                "source": "astraa_local_simulation",
                "raw": {
                    "ticket": ticket,
                    "environment": env,
                    "simulation": True
                },
                "reason": "Local QA simulated payment verified."
            }

        return {
            "verified": False,
            "source": "astraa_local_simulation",
            "raw": {
                "ticket": ticket,
                "environment": env,
                "simulation": True
            },
            "reason": "Local QA simulation only accepts ASTRAA-QA-* or QA-* tickets."
        }

    store_id = os.getenv("MONERIS_STORE_ID")
    api_token = os.getenv("MONERIS_API_TOKEN")
    checkout_id = os.getenv("MONERIS_CHECKOUT_ID")

    missing = []
    if not store_id:
        missing.append("MONERIS_STORE_ID")
    if not api_token:
        missing.append("MONERIS_API_TOKEN")
    if not checkout_id:
        missing.append("MONERIS_CHECKOUT_ID")

    if missing:
        return {
            "verified": False,
            "source": "moneris_receipt_request",
            "raw": {},
            "reason": "Missing backend Moneris env vars: " + ", ".join(missing)
        }

    url = MONERIS_RECEIPT_URLS.get(env, MONERIS_RECEIPT_URLS["qa"])

    request_payload = {
        "store_id": store_id,
        "api_token": api_token,
        "checkout_id": checkout_id,
        "ticket": ticket,
        "environment": "prod" if env == "prod" else "qa",
        "action": "receipt"
    }

    try:
        response = requests.post(url, json=request_payload, timeout=20)
        raw = response.json() if response.content else {}

        # Moneris response schemas can contain nested response objects depending on setup.
        # Receipt request success means the lookup succeeded; payment approval must be verified separately.
        response_obj = raw.get("response", {}) if isinstance(raw, dict) else {}
        success_value = str(response_obj.get("success", "")).lower()

        receipt_request_ok = success_value == "true"
        approved, approval_reason = astraa_moneris_receipt_approved(raw)

        verified = bool(receipt_request_ok and approved)

        return {
            "verified": verified,
            "approved": approved,
            "receipt_request_ok": receipt_request_ok,
            "source": "moneris_receipt_request",
            "raw": raw,
            "reason": (
                "Moneris receipt verified and transaction approved."
                if verified
                else "Moneris receipt request did not prove an approved transaction: " + approval_reason
            )
        }

    except Exception as exc:
        return {
            "verified": False,
            "source": "moneris_receipt_request",
            "raw": {},
            "reason": "Moneris receipt request failed: " + str(exc)
        }


def astraa_apply_verified_payment_to_usage(account_email, purchase_type, selected_plan, payment_record):
    """
    Updates astraa_usage_db.json after verified payment only.
    """
    account_email = str(account_email or "").strip().lower()
    selected_plan = str(selected_plan or "").strip()
    purchase_type = str(purchase_type or "").strip()

    db = astraa_storage_load_usage_db()

    if not account_email:
        return False, "Missing account email.", None

    # Determine target plan.
    if purchase_type == "subscription_basic":
        selected_plan = "Basic"
    elif purchase_type == "subscription_professional":
        selected_plan = "Professional"

    if account_email not in db:
        db[account_email] = astraa_default_usage_record(account_email, selected_plan or "Trial")

    record = db[account_email]

    record["account_id"] = account_email
    record["primary_email"] = account_email
    record["selected_tool"] = "Astraa Estimator"

    if purchase_type == "subscription_basic":
        record["selected_plan"] = "Basic"
        record["selected_price"] = "$39.99 CAD/month"
        record["payment_status"] = "active"
        record["subscription_status"] = "active"
        record["estimate_limit"] = 30
        record["billing_period_key"] = astraa_month_key()
        record["billing_period_start"] = astraa_month_start()
        record["billing_period_end"] = astraa_month_end()

    elif purchase_type == "subscription_professional":
        record["selected_plan"] = "Professional"
        record["selected_price"] = "$99.99 CAD/month"
        record["payment_status"] = "active"
        record["subscription_status"] = "active"
        record["estimate_limit"] = 120
        record["billing_period_key"] = astraa_month_key()
        record["billing_period_start"] = astraa_month_start()
        record["billing_period_end"] = astraa_month_end()

    elif purchase_type == "estimate_pack_10":
        # Estimate pack should only be useful for paid active accounts.
        if record.get("payment_status") != "active" or record.get("subscription_status") != "active":
            return False, "Estimate pack cannot be applied to inactive account.", record

        record["extra_estimate_credits_total"] = int(record.get("extra_estimate_credits_total") or 0) + 10

    else:
        return False, "Unsupported purchase_type.", record

    record.setdefault("payment_history", [])
    record["payment_history"].append({
        "payment_id": payment_record.get("payment_id"),
        "purchase_type": purchase_type,
        "selected_plan": record.get("selected_plan"),
        "verified_at": payment_record.get("verified_at"),
        "source": payment_record.get("verification_source"),
        "ticket_reference": payment_record.get("ticket_reference")
    })

    record["updated_at"] = astraa_payment_now()

    record = astraa_normalize_usage_record(record)

    db[account_email] = record
    astraa_storage_save_usage_db(db)

    return True, "Usage record updated after verified payment.", record


@app.post("/api/payment/verify-moneris-receipt")
def astraa_verify_moneris_receipt_route():
    raw_payload = request.get_json(silent=True)

    if raw_payload is None:
        return jsonify({
            "status": "rejected",
            "gateway": "Astraa Gateway",
            "errors": ["Invalid or missing JSON payload."]
        }), 400

    payload = astraa_sanitize(raw_payload)

    # ASTRAA_ACCOUNT_AUTHORITY_ROUTE_WIRING_V1
    account_authority = astraa_resolve_account_authority(payload, request)

    if not account_authority.get("allowed"):
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "payment_verified": False,
            "reason": account_authority.get("reason"),
            "identity_source": account_authority.get("identity_source"),
            "review_note": "Payment verification blocked by account authority guard."
        }), 403

    account_email = account_authority.get("account_email")

    selected_tool = payload.get("selected_tool") or "Astraa Estimator"
    selected_plan = payload.get("selected_plan") or payload.get("plan") or ""
    purchase_type = payload.get("purchase_type") or ""
    ticket = payload.get("moneris_ticket") or payload.get("ticket") or ""

    if selected_tool != "Astraa Estimator":
        return jsonify({
            "status": "rejected",
            "gateway": "Astraa Gateway",
            "errors": ["Only Astraa Estimator payment verification is supported in this route version."]
        }), 400

    account_email_normalized = str(account_email or "").strip().lower()
    idempotency_key = astraa_payment_idempotency_key(
        account_email_normalized,
        purchase_type,
        ticket
    )

    # ASTRAA_PAYMENT_STORAGE_WRAPPER_ADOPTION_V1
    payment_db = astraa_storage_load_payment_db()
    existing_verified_payment = astraa_find_verified_payment_by_idempotency(
        payment_db,
        idempotency_key
    )

    if existing_verified_payment:
        return jsonify({
            "status": "ok",
            "gateway": "Astraa Gateway",
            "payment_verified": True,
            "idempotent_replay": True,
            "reason": "Payment was already verified and applied. No duplicate usage update was performed.",
            "payment": existing_verified_payment,
            "usage": astraa_usage_summary_for_account(account_email_normalized),
            "review_note": "Backend idempotency prevented duplicate payment application."
        }), 200

    # ASTRAA_PAYMENT_SCHEMA_VALIDATION_ROUTE_GUARD_V2
    # Validate payment verification input before calling Moneris receipt verification
    # or creating a payment record.
    valid_payment_payload, payment_payload_errors, clean_payment_payload = astraa_validate_payment_verification_payload(payload)

    if not valid_payment_payload:
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "payment_verified": False,
            "reason": "Invalid payment verification input.",
            "errors": payment_payload_errors,
            "review_note": "Payment verification blocked by schema validation before Moneris receipt verification."
        }), 400

    payload.update(clean_payment_payload)

    selected_tool = payload.get("selected_tool") or "Astraa Estimator"
    selected_plan = payload.get("selected_plan") or selected_plan
    purchase_type = payload.get("purchase_type") or purchase_type
    ticket = payload.get("moneris_ticket") or ticket

    verification = astraa_verify_moneris_receipt(ticket)

    payment_record = {
        "payment_id": astraa_payment_record_id(),
        "idempotency_key": idempotency_key,
        "idempotent_replay": False,
        "account_email": account_email_normalized,
        "selected_tool": selected_tool,
        "selected_plan": selected_plan,
        "purchase_type": purchase_type,
        "ticket_reference": str(ticket)[-12:] if ticket else "",
        "verified": bool(verification.get("verified")),
        "receipt_approved": bool(verification.get("approved")),
        "receipt_request_ok": bool(verification.get("receipt_request_ok")),
        "verification_source": verification.get("source"),
        "verification_reason": verification.get("reason"),
        "verified_at": astraa_payment_now() if verification.get("verified") else None,
        "environment": astraa_moneris_env(),
        "created_at": astraa_payment_now()
    }

    payment_db.append(payment_record)
    astraa_storage_save_payment_db(payment_db)

    if not verification.get("verified"):
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "payment_verified": False,
            "reason": verification.get("reason"),
            "payment": payment_record,
            "review_note": "Payment was not verified. Account access was not changed."
        }), 403

    applied, apply_reason, usage_record = astraa_apply_verified_payment_to_usage(
        account_email,
        purchase_type,
        selected_plan,
        payment_record
    )

    if not applied:
        return jsonify({
            "status": "blocked",
            "gateway": "Astraa Gateway",
            "payment_verified": True,
            "reason": apply_reason,
            "payment": payment_record,
            "usage": usage_record,
            "review_note": "Payment verified but usage update was not applied."
        }), 400

    return jsonify({
        "status": "ok",
        "gateway": "Astraa Gateway",
        "payment_verified": True,
        "payment": payment_record,
        "usage": {
            "account_id": usage_record.get("account_id"),
            "selected_plan": usage_record.get("selected_plan"),
            "payment_status": usage_record.get("payment_status"),
            "subscription_status": usage_record.get("subscription_status"),
            "estimate_limit": usage_record.get("estimate_limit"),
            "estimate_used": usage_record.get("estimate_used"),
            "extra_estimate_credits_total": usage_record.get("extra_estimate_credits_total"),
            "extra_estimate_credits_used": usage_record.get("extra_estimate_credits_used"),
            "billing_period_key": usage_record.get("billing_period_key")
        },
        "review_note": "Backend payment verification completed. Production mode requires real Moneris env vars and receipt validation."
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
