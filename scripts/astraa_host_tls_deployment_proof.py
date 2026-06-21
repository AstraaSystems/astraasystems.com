#!/usr/bin/env python3
"""
Astraa Host/TLS Deployment Proof

READ-ONLY SCRIPT.

Purpose:
- Verify local deployment-readiness files and settings before any deployed Moneris regression.
- Confirm Host/TLS proof requirements are represented in the repo.
- Avoid connecting to production or changing runtime behavior.

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

from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "scripts/astraa_host_tls_deployment_proof_plan.py",
    "scripts/astraa_wsgi_deployment_inventory.py",
    "scripts/astraa_wsgi_deployment_plan.py",
    "scripts/astraa_cors_hardening_proof.py",
    "scripts/astraa_secure_secret_presence_check_proof.py",
    "scripts/astraa_post_auth_hardening_proof.py",
]


REQUIRED_TEXT_CHECKS = {
    "scripts/astraa_host_tls_deployment_proof_plan.py": [
        "Do not expose Flask development server publicly.",
        "Run Astraa API through Gunicorn/WSGI or an equivalent managed production runtime.",
        "Serve public website and API over HTTPS/TLS.",
        "Use final allowed origins for CORS.",
        "Keep ASTRAA_PUBLIC_LAUNCH_MODE=true on production-style runtime.",
        "Keep ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE unset or false on production host.",
    ],
}


def section(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def pass_line(message: str) -> None:
    print("[PASS]", message)


def fail_line(message: str) -> None:
    print("[FAIL]", message)


def main() -> int:
    failures: list[str] = []

    section("ASTRAA HOST/TLS DEPLOYMENT PROOF")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Repo root:", ROOT)

    section("REQUIRED FILE CHECKS")
    for relative_path in REQUIRED_FILES:
        path = ROOT / relative_path
        if path.exists():
            pass_line(f"Found {relative_path}")
        else:
            failures.append(f"Missing {relative_path}")
            fail_line(f"Missing {relative_path}")

    section("REQUIRED HOST/TLS PLAN TEXT CHECKS")
    for relative_path, required_phrases in REQUIRED_TEXT_CHECKS.items():
        path = ROOT / relative_path
        if not path.exists():
            failures.append(f"Cannot inspect missing file {relative_path}")
            fail_line(f"Cannot inspect missing file {relative_path}")
            continue

        text = path.read_text(encoding="utf-8")
        for phrase in required_phrases:
            if phrase in text:
                pass_line(f"{relative_path} contains: {phrase}")
            else:
                failures.append(f"{relative_path} missing phrase: {phrase}")
                fail_line(f"{relative_path} missing phrase: {phrase}")

    section("SAFETY CONFIRMATION")
    print("This proof did not deploy Astraa.")
    print("This proof did not start services.")
    print("This proof did not modify Nginx/systemd.")
    print("This proof did not request TLS certificates.")
    print("This proof did not connect to production host.")
    print("This proof did not change backend/auth/payment behavior.")
    print("This proof did not run Moneris payments.")

    section("RESULT")
    if failures:
        print("HOST/TLS DEPLOYMENT PROOF: FAIL")
        print("Failures:")
        for failure in failures:
            print("-", failure)
        return 1

    print("HOST/TLS DEPLOYMENT PROOF: PASS")
    print("Host/TLS deployment proof artifacts are present and guarded.")
    print("Next blocker after this lane: deployed health/CORS smoke proof once final host/subdomain exists.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
