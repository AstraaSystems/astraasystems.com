#!/usr/bin/env python3
"""
Astraa Patch: CORS Domain Lock

PATCH SCRIPT.

Purpose:
- Add strict public-launch-mode CORS allowlist behavior.
- Preserve localhost/internal QA only when ASTRAA_ALLOW_LOCALHOST_CORS=true.
- Insert before CORS(app...) so this after_request hook runs after Flask-CORS and can override wildcard headers.

Safety:
- Creates timestamped backup of api.py.
- Idempotent marker.
- Does not touch auth/payment/Estimator/Moneris/staging DB logic.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime


API_PATH = Path("api.py")
MARKER = "ASTRAA_CORS_DOMAIN_LOCK_V1"

BLOCK = r'''

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

'''


def main():
    if not API_PATH.exists():
        raise SystemExit("❌ api.py not found")

    text = API_PATH.read_text(encoding="utf-8", errors="ignore")

    if MARKER in text:
        print("✅ CORS domain lock already exists")
        return

    cors_pos = text.find("CORS(app")
    if cors_pos == -1:
        raise SystemExit("❌ Could not find CORS(app...) call in api.py")

    backup = API_PATH.with_name(
        API_PATH.name + ".bak_cors_domain_lock_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    backup.write_text(text, encoding="utf-8")

    patched = text[:cors_pos] + BLOCK + "\n" + text[cors_pos:]
    API_PATH.write_text(patched, encoding="utf-8")

    print("✅ Added public-launch-mode CORS domain lock")
    print(f"Inserted before CORS(app...) at index: {cors_pos}")
    print(f"Backup: {backup}")


if __name__ == "__main__":
    main()
