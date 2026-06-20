#!/usr/bin/env python3
"""
Astraa Gunicorn Command Template

READ-ONLY SCRIPT.

Purpose:
- Print safe Gunicorn command templates for Astraa WSGI deployment.
- Document local staging / production-style environment variables.
- Keep deployment actions manual and intentional.

Does NOT:
- start Gunicorn
- start production services
- create systemd files
- create nginx files
- modify api.py
- modify wsgi.py
- deploy Astraa
- change secrets
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def print_block(text):
    print(text.strip())


def main():
    section("ASTRAA GUNICORN COMMAND TEMPLATE")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Repository root:", ROOT)

    section("ASSUMED WSGI ENTRYPOINT")
    print_block("""
wsgi.py should expose:

from api import app
application = app

Gunicorn target:
wsgi:app
""")

    section("LOCAL STAGING / PRODUCTION-STYLE ENVIRONMENT")
    print_block("""
export ASTRAA_STORAGE_BACKEND=json
export ASTRAA_PUBLIC_LAUNCH_MODE=true
export ASTRAA_REQUEST_GUARD_ENABLED=true
export ASTRAA_ALLOWED_ORIGINS="https://astraasystems.com,https://www.astraasystems.com"
export ASTRAA_ALLOW_LOCALHOST_CORS=false
unset ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE
unset ASTRAA_ALLOW_STAGING_IMPORT
unset ASTRAA_ALLOW_STAGING_DB_CREATE
""")

    section("INTERNAL QA OVERRIDE ENVIRONMENT")
    print_block("""
# Use only for intentional internal QA/regression testing.
export ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true
export ASTRAA_ALLOW_LOCALHOST_CORS=true
""")

    section("BASIC GUNICORN COMMAND — LOCAL PRODUCTION-STYLE")
    print_block("""
gunicorn \
  --bind 127.0.0.1:5000 \
  --workers 2 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
""")

    section("BASIC GUNICORN COMMAND — BEHIND REVERSE PROXY")
    print_block("""
gunicorn \
  --bind 127.0.0.1:8001 \
  --workers 2 \
  --threads 2 \
  --timeout 120 \
  --forwarded-allow-ips="127.0.0.1" \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
""")

    section("OPTIONAL SMOKE TESTS AFTER STARTING GUNICORN")
    print_block("""
curl -i -s "http://127.0.0.1:5000/health" \
  -H "Origin: https://astraasystems.com" | head -n 30

python3 scripts/astraa_cors_acceptance_tests.py
python3 scripts/astraa_post_auth_hardening_proof.py
python3 scripts/astraa_staging_pipeline_proof.py
""")

    section("PRODUCTION SAFETY NOTES")
    print_block("""
- Do not expose Flask development server directly to the public.
- Do not enable ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE in production.
- Do not enable ASTRAA_ALLOW_LOCALHOST_CORS in production.
- Do not deploy with wildcard CORS.
- Do not commit Moneris credentials.
- Load MONERIS_STORE_ID, MONERIS_API_TOKEN, and MONERIS_CHECKOUT_ID from secure environment.
- Keep JSON/JSONL storage only for controlled staging/internal proof until managed DB cutover is planned.
- Use a reverse proxy or managed platform TLS layer for HTTPS.
""")

    section("READ-ONLY CONFIRMATION")
    print("This script did not start Gunicorn.")
    print("This script did not create services.")
    print("This script did not create reverse-proxy configs.")
    print("This script did not modify api.py or wsgi.py.")
    print("This script did not deploy Astraa.")
    print("This script did not change secrets or data.")


if __name__ == "__main__":
    main()
