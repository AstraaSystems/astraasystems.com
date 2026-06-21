#!/usr/bin/env python3
"""
Astraa Host/TLS Deployment Proof Plan

READ-ONLY SCRIPT.

Purpose:
- Define the Host/TLS deployment proof required before deployed Moneris regression.
- Keep deployment planning separate from actually deploying Astraa.
- Confirm production should use WSGI/Gunicorn or managed runtime, reverse proxy/TLS, locked CORS,
  secure secrets, and dev-login disabled.

Does NOT:
- deploy Astraa
- start services
- modify Nginx/systemd
- request TLS certificates
- connect to production host
- change backend/auth/payment behavior
- run Moneris payments
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
    section("ASTRAA HOST/TLS DEPLOYMENT PROOF PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("CURRENT STATUS")
    print("Secure secret presence checks are now available.")
    print("Next blocker before deployed Moneris regression: Host/TLS deployment proof.")

    section("DEPLOYMENT REQUIREMENTS")
    print_list([
        "Do not expose Flask development server publicly.",
        "Run Astraa API through Gunicorn/WSGI or an equivalent managed production runtime.",
        "Place Nginx or a managed reverse proxy in front of the API.",
        "Serve public website and API over HTTPS/TLS.",
        "Use final allowed origins for CORS.",
        "Load real secrets from secure host environment or secret manager only.",
        "Keep ASTRAA_PUBLIC_LAUNCH_MODE=true on production-style runtime.",
        "Keep ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE unset or false on production host.",
    ])

    section("PROOF TARGETS")
    print_list([
        "Public website loads over HTTPS.",
        "Backend /health or equivalent health endpoint responds over HTTPS.",
        "Reverse proxy forwards headers correctly.",
        "CORS permits only approved Astraa origins.",
        "Dev-login is blocked in public launch mode.",
        "Secure secret presence check runs without printing values.",
        "No real secrets are committed to git.",
        "No customer access is broadly opened by deployment proof.",
    ])

    section("NO-GO CONDITIONS")
    print_list([
        "Flask dev server exposed publicly.",
        "HTTP-only production API.",
        "Wildcard CORS in production.",
        "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true on production host.",
        "Real secrets stored in git-tracked files.",
        "Payment auto-unlock tested before deployed Moneris regression.",
    ])

    section("NEXT IMPLEMENTATION ARTIFACTS")
    print_list([
        "scripts/astraa_host_tls_deployment_proof.py",
        "scripts/astraa_host_tls_env_template_check.py",
        "Optional later: deployed health/CORS smoke script once final host/subdomain is chosen.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not deploy Astraa.")
    print("This script did not start services.")
    print("This script did not modify Nginx/systemd.")
    print("This script did not request TLS certificates.")
    print("This script did not connect to production host.")
    print("This script did not change backend/auth/payment behavior.")
    print("This script did not run Moneris payments.")


if __name__ == "__main__":
    main()
