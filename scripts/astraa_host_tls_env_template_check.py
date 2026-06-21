#!/usr/bin/env python3
"""
Astraa Host/TLS Environment Template Check

READ-ONLY SCRIPT.

Purpose:
- Check that production-style environment template guidance includes Host/TLS deployment requirements.
- Confirm required flags are represented before deployed health/CORS smoke proof.
- Avoid reading, printing, or validating real secret values.

Does NOT:
- deploy Astraa
- start services
- modify Nginx/systemd
- request TLS certificates
- connect to production host
- change backend/auth/payment behavior
- run Moneris payments
- print secret values
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


CANDIDATE_TEMPLATE_FILES = [
    ".env.production.example",
    ".env.production.template",
    ".env.example",
    "config/.env.production.example",
    "config/.env.production.template",
    "docs/production.env.example",
    "docs/production-env-template.md",
]


REQUIRED_TERMS = [
    "ASTRAA_PUBLIC_LAUNCH_MODE",
    "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE",
    "ALLOWED_ORIGINS",
    "CORS",
    "HTTPS",
    "TLS",
]


def section(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def pass_line(message: str) -> None:
    print("[PASS]", message)


def warn_line(message: str) -> None:
    print("[WARN]", message)


def fail_line(message: str) -> None:
    print("[FAIL]", message)


def main() -> int:
    failures: list[str] = []

    section("ASTRAA HOST/TLS ENVIRONMENT TEMPLATE CHECK")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Repo root:", ROOT)

    section("TEMPLATE DISCOVERY")
    existing_templates = []

    for relative_path in CANDIDATE_TEMPLATE_FILES:
        path = ROOT / relative_path
        if path.exists():
            existing_templates.append(path)
            pass_line(f"Found template candidate: {relative_path}")

    if not existing_templates:
        warn_line("No standard production environment template file found.")
        warn_line("This is not automatically unsafe, but a guarded template should be added before deployment.")
        failures.append("Missing production-style environment template file.")

    section("REQUIRED TERM CHECKS")
    combined_text = ""

    for path in existing_templates:
        try:
            combined_text += "\n" + path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"Could not read template as UTF-8: {path.relative_to(ROOT)}")
            fail_line(f"Could not read template as UTF-8: {path.relative_to(ROOT)}")

    for term in REQUIRED_TERMS:
        if term in combined_text:
            pass_line(f"Template guidance includes: {term}")
        else:
            failures.append(f"Template guidance missing: {term}")
            fail_line(f"Template guidance missing: {term}")

    section("SECRET SAFETY CONFIRMATION")
    print("This check did not print secret values.")
    print("This check did not require real secret values.")
    print("This check only inspected template/guidance files.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not deploy Astraa.")
    print("This script did not start services.")
    print("This script did not modify Nginx/systemd.")
    print("This script did not request TLS certificates.")
    print("This script did not connect to production host.")
    print("This script did not change backend/auth/payment behavior.")
    print("This script did not run Moneris payments.")

    section("RESULT")
    if failures:
        print("HOST/TLS ENV TEMPLATE CHECK: FAIL")
        print("Failures:")
        for failure in failures:
            print("-", failure)
        return 1

    print("HOST/TLS ENV TEMPLATE CHECK: PASS")
    print("Production-style Host/TLS environment template guidance is represented.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
