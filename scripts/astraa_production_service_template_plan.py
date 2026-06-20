#!/usr/bin/env python3
"""
Astraa Production Service Template Plan

READ-ONLY SCRIPT.

Purpose:
- Plan production service templates for Gunicorn + reverse proxy deployment.
- Define systemd, Nginx/reverse proxy, environment, logging, restart, and health-check strategy.
- Do not create actual service/proxy files yet.

Does NOT:
- create systemd files
- create nginx files
- start services
- deploy Astraa
- modify api.py
- modify wsgi.py
- change secrets
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
    section("ASTRAA PRODUCTION SERVICE TEMPLATE PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("CURRENT PROOF")
    print_list([
        "wsgi.py entrypoint exists.",
        "requirements.txt includes gunicorn.",
        "Gunicorn local smoke test passed with wsgi:app.",
        "CORS public-origin header worked through Gunicorn.",
        "Dev-login is blocked by default in public launch mode.",
        "Internal QA override remains explicit.",
    ])

    section("TARGET SERVICE SHAPE")
    print_list([
        "Gunicorn runs Astraa API using wsgi:app.",
        "Gunicorn binds to localhost only, e.g. 127.0.0.1:8001.",
        "Nginx or managed reverse proxy forwards public HTTPS traffic to Gunicorn.",
        "TLS/HTTPS terminates at reverse proxy or managed platform.",
        "The Flask development server is never exposed publicly.",
    ])

    section("SYSTEMD SERVICE TEMPLATE PLAN")
    print_list([
        "Service name: astraa-api.service.",
        "Working directory: /home/keshanth/ARKA/ardhanarishvara or deployment path.",
        "ExecStart: venv/bin/gunicorn --bind 127.0.0.1:8001 --workers 2 --threads 2 --timeout 120 wsgi:app.",
        "Restart: on-failure.",
        "Environment variables loaded from a secure env file outside git.",
        "User/group should be a non-root deployment user.",
        "Logs should go to journald or configured log files.",
    ])

    section("NGINX / REVERSE PROXY TEMPLATE PLAN")
    print_list([
        "Server name: api.astraasystems.com or chosen backend subdomain.",
        "Listen on 443 with TLS certificate.",
        "Proxy pass to http://127.0.0.1:8001.",
        "Forward Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto.",
        "Set appropriate client/body/proxy timeouts for Moneris/preload/payment routes.",
        "Do not proxy unknown public domains.",
    ])

    section("PRODUCTION ENVIRONMENT PLAN")
    print_list([
        "ASTRAA_PUBLIC_LAUNCH_MODE=true",
        "ASTRAA_REQUEST_GUARD_ENABLED=true",
        "ASTRAA_ALLOWED_ORIGINS=https://astraasystems.com,https://www.astraasystems.com",
        "ASTRAA_ALLOW_LOCALHOST_CORS=false",
        "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=false or unset",
        "ASTRAA_STORAGE_BACKEND=json only for controlled staging; managed DB later.",
        "MONERIS credentials loaded from secure environment, not git.",
    ])

    section("DEPLOYMENT ACCEPTANCE TESTS")
    print_list([
        "curl /health through public API domain returns status ok.",
        "Allowed Astraa origin receives matching Access-Control-Allow-Origin.",
        "Unknown origin is not wildcard-allowed.",
        "Dev-login is blocked without internal override.",
        "Auth acceptance block-mode passes.",
        "Internal QA override works only when explicitly enabled.",
        "Estimator active account regression passes.",
        "Preload/payment verification regression passes.",
        "Gunicorn service restarts cleanly after stop/start.",
    ])

    section("DO NOT DO YET")
    print_list([
        "Do not create systemd/nginx files until target host/subdomain is chosen.",
        "Do not commit production secrets.",
        "Do not expose Gunicorn directly to public internet.",
        "Do not enable dev-login override in production.",
        "Do not onboard broad customer traffic before production auth provider is selected.",
    ])

    section("NEXT SAFE STEP")
    print("Create disabled template files or scripts that print systemd/nginx templates without installing them.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not create service files.")
    print("This script did not create reverse-proxy files.")
    print("This script did not start services.")
    print("This script did not deploy Astraa.")
    print("This script did not modify secrets or data.")


if __name__ == "__main__":
    main()
