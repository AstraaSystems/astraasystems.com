#!/usr/bin/env python3
"""
Astraa Production Deployment / WSGI Plan

READ-ONLY SCRIPT.

Purpose:
- Plan the move from Flask development server to production WSGI deployment.
- Define deployment target, environment variables, process manager, reverse proxy,
  TLS, secrets, logs, health checks, and acceptance tests.

Does NOT:
- modify api.py
- start production services
- create systemd files
- create nginx/apache files
- deploy to a server
- change secrets
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
    section("ASTRAA PRODUCTION DEPLOYMENT / WSGI PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("CURRENT STATE")
    print_list([
        "api.py currently runs through Flask development server during local QA.",
        "Local staging DB proof is complete.",
        "Dev-login is blocked in public launch mode unless internal QA override is explicitly enabled.",
        "CORS/domain allowlist is patched for public launch mode.",
        "Post-auth-hardening and staging pipeline proofs are available as one-command scripts.",
    ])

    section("TARGET PRODUCTION SHAPE")
    print_list([
        "Run Astraa API through a WSGI server instead of Flask development server.",
        "Use Gunicorn or uWSGI as the Python WSGI process.",
        "Place Nginx or equivalent reverse proxy in front of WSGI.",
        "Terminate HTTPS/TLS at reverse proxy or managed platform layer.",
        "Serve static/public website through the existing web host or reverse proxy.",
        "Keep API backend behind production domain/subdomain.",
    ])

    section("RECOMMENDED INITIAL DEPLOYMENT MODEL")
    print_list([
        "Use a dedicated API host/subdomain such as api.astraasystems.com or backend.astraasystems.com.",
        "Use Gunicorn for WSGI process management initially.",
        "Use Nginx as reverse proxy if deploying to a VPS/server.",
        "Use systemd or platform process manager to restart the API service.",
        "Keep local SQLite staging proof separate from any future managed production DB.",
        "Do not expose Flask dev server directly to public traffic.",
    ])

    section("WSGI ENTRYPOINT PLAN")
    print_list([
        "Create a small wsgi.py entrypoint that imports the Flask app from api.py.",
        "Confirm api.py exposes app = Flask(__name__).",
        "Run with gunicorn wsgi:app rather than python3 api.py.",
        "Keep python3 api.py available only for local/internal QA.",
    ])

    section("ENVIRONMENT VARIABLES TO DEFINE")
    print_list([
        "ASTRAA_PUBLIC_LAUNCH_MODE=true",
        "ASTRAA_REQUEST_GUARD_ENABLED=true",
        "ASTRAA_STORAGE_BACKEND=json initially, until managed DB cutover is planned.",
        "ASTRAA_ALLOWED_ORIGINS=https://astraasystems.com,https://www.astraasystems.com",
        "ASTRAA_ALLOW_LOCALHOST_CORS=false in production.",
        "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=false or unset in production.",
        "MONERIS_ENV=prod after final confirmation.",
        "MONERIS_STORE_ID, MONERIS_API_TOKEN, MONERIS_CHECKOUT_ID loaded from secure environment, not committed files.",
    ])

    section("SECRETS MANAGEMENT PLAN")
    print_list([
        "Do not commit Moneris credentials.",
        "Do not store production secrets in frontend files.",
        "Use server environment, deployment secret store, or managed platform secret manager.",
        "Audit logs should not print raw full secrets.",
        "Payment logs should keep safe ticket references but avoid sensitive raw payload exposure.",
    ])

    section("REVERSE PROXY / TLS PLAN")
    print_list([
        "Force HTTPS for production domain.",
        "Forward X-Forwarded-For and X-Forwarded-Proto correctly.",
        "Set proxy timeout appropriate for payment/preload calls.",
        "Restrict exposed ports so Gunicorn is not directly public if using Nginx.",
        "Confirm CORS allowlist uses the final public origin exactly.",
    ])

    section("PROCESS MANAGEMENT PLAN")
    print_list([
        "Use systemd or platform service manager to start/restart Gunicorn.",
        "Configure restart-on-failure.",
        "Capture stdout/stderr logs.",
        "Keep deployment logs separate from customer data.",
        "Add health-check endpoint monitoring for /health.",
    ])

    section("DATA / STORAGE PLAN")
    print_list([
        "Keep JSON/JSONL source-of-truth only for controlled staging/internal phase.",
        "Do not onboard broad customer production data into local JSON files.",
        "Use local staging SQLite proof only as proof, not final production DB.",
        "Before broad public production, select managed DB and migrate reviewed records through guarded flow.",
    ])

    section("ACCEPTANCE TESTS BEFORE PRODUCTION DEPLOYMENT")
    print_list([
        "python3 -m py_compile api.py passes.",
        "scripts/astraa_post_auth_hardening_proof.py passes.",
        "scripts/astraa_cors_hardening_proof.py passes.",
        "scripts/astraa_staging_pipeline_proof.py passes.",
        "Allowed origin returns Access-Control-Allow-Origin matching Astraa domain.",
        "Unknown origin is not wildcard-allowed.",
        "Dev-login is blocked without explicit internal override.",
        "Estimator paid account regression passes.",
        "Payment verify idempotent replay passes.",
        "Moneris preload returns success from deployed API domain.",
    ])

    section("DO NOT DO YET")
    print_list([
        "Do not publish broad customer Workspace access until production auth provider is selected.",
        "Do not point real customers to Flask development server.",
        "Do not migrate broad production customer data into local SQLite.",
        "Do not enable dev-login override in production environment.",
        "Do not deploy with wildcard CORS.",
    ])

    section("NEXT SAFE STEPS")
    print_list([
        "Step 1: Add WSGI/deployment inventory script.",
        "Step 2: Add wsgi.py entrypoint in a small reversible patch.",
        "Step 3: Add Gunicorn command template script/document.",
        "Step 4: Add Nginx/systemd template documents, disabled by default.",
        "Step 5: Run post-auth and CORS proofs after every deployment-related change.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not create deployment files.")
    print("This script did not start services.")
    print("This script did not deploy Astraa.")
    print("This script did not change secrets or data.")


if __name__ == "__main__":
    main()
