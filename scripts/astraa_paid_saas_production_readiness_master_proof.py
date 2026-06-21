#!/usr/bin/env python3
"""
Astraa Paid SaaS Production Readiness Master Proof

READ-ONLY SCRIPT.

Purpose:
- Summarize required paid SaaS production-readiness proof artifacts.
- Confirm that planning, guards, and smoke proof skeletons exist.
- Keep marketing launch readiness separate from paid SaaS production activation.
- Show remaining deployed-runtime blockers before paid SaaS can be activated.

Does NOT:
- deploy Astraa
- start services
- modify Nginx/systemd
- request TLS certificates
- print secrets
- connect to Moneris
- run Moneris payments
- change backend/auth/payment behavior
- unlock customer access
- activate paid SaaS production mode
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_ARTIFACTS = [
    "scripts/astraa_public_launch_paid_lead_capture_proof.py",
    "scripts/astraa_paid_onboarding_followup_proof.py",
    "scripts/astraa_secure_secret_presence_check_proof.py",
    "scripts/astraa_host_tls_deployment_proof_plan.py",
    "scripts/astraa_host_tls_deployment_proof.py",
    "scripts/astraa_host_tls_env_template_check.py",
    ".env.production.example",
    "scripts/astraa_deployed_host_smoke_proof.py",
    "scripts/astraa_deployed_cors_smoke_proof.py",
    "scripts/astraa_deployed_moneris_regression_plan.py",
    "scripts/astraa_deployed_moneris_regression_guard.py",
    "scripts/astraa_paid_saas_activation_decision_guard.py",
    "scripts/astraa_final_deployment_target_decision_guard.py",
]


REQUIRED_MARKETING_PAID_SEPARATION_TERMS = {
    "scripts/astraa_public_launch_paid_lead_capture_proof.py": [
        "paid",
        "lead",
    ],
    "scripts/astraa_paid_saas_activation_decision_guard.py": [
        "ASTRAA_FINAL_OPERATOR_APPROVAL_CONFIRMED",
        "PAID SAAS ACTIVATION DECISION",
    ],
    "scripts/astraa_deployed_moneris_regression_guard.py": [
        "ASTRAA_DEPLOYED_HOST_TLS_SMOKE_PASSED",
        "ASTRAA_DEPLOYED_CORS_SMOKE_PASSED",
        "ASTRAA_MONERIS_CONTROLLED_TEST_ACCOUNT_CONFIRMED",
    ],
    "scripts/astraa_final_deployment_target_decision_guard.py": [
        "ASTRAA_FINAL_DEPLOYMENT_TARGET_CONFIRMED",
        "FINAL DEPLOYMENT TARGET DECISION",
        "ASTRAA_DEPLOYED_BASE_URL",
    ],
}


REMAINING_DEPLOYED_BLOCKERS = [
    "Choose final production or production-style host/subdomain.",
    "Deploy public website/API over HTTPS/TLS.",
    "Run deployed Host/TLS smoke proof against final URL.",
    "Run deployed CORS smoke proof against final URL and approved origin.",
    "Confirm deployed auth gate.",
    "Confirm deployed managed DB gate.",
    "Confirm deployed secret presence gate without printing values.",
    "Run one controlled deployed Moneris regression only after guards pass.",
    "Confirm inactive/unpaid accounts remain blocked.",
    "Confirm declined/failed payment path does not unlock access.",
    "Confirm only controlled approved account unlocks.",
    "Set final operator approval only after all previous proofs pass.",
]


def section(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def pass_line(message: str) -> None:
    print("[PASS]", message)


def fail_line(message: str) -> None:
    print("[FAIL]", message)


def print_list(items: list[str]) -> None:
    for item in items:
        print("-", item)


def main() -> int:
    failures: list[str] = []

    section("ASTRAA PAID SAAS PRODUCTION READINESS MASTER PROOF")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Repo root:", ROOT)

    section("REQUIRED ARTIFACT CHECKS")
    for relative_path in REQUIRED_ARTIFACTS:
        path = ROOT / relative_path
        if path.exists():
            pass_line(f"Found {relative_path}")
        else:
            failures.append(f"Missing {relative_path}")
            fail_line(f"Missing {relative_path}")

    section("KEY TERM CHECKS")
    for relative_path, required_terms in REQUIRED_MARKETING_PAID_SEPARATION_TERMS.items():
        path = ROOT / relative_path
        if not path.exists():
            failures.append(f"Cannot inspect missing file {relative_path}")
            fail_line(f"Cannot inspect missing file {relative_path}")
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        for term in required_terms:
            if term in text:
                pass_line(f"{relative_path} contains: {term}")
            else:
                failures.append(f"{relative_path} missing required term: {term}")
                fail_line(f"{relative_path} missing required term: {term}")

    section("REMAINING DEPLOYED-RUNTIME BLOCKERS")
    print_list(REMAINING_DEPLOYED_BLOCKERS)

    section("SAFETY CONFIRMATION")
    print("This master proof did not inspect or print secret values.")
    print("This master proof did not connect to deployed infrastructure.")
    print("This master proof did not run payment tests.")
    print("This master proof only checked local repo proof artifacts.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not deploy Astraa.")
    print("This script did not start services.")
    print("This script did not modify Nginx/systemd.")
    print("This script did not request TLS certificates.")
    print("This script did not print secrets.")
    print("This script did not connect to Moneris.")
    print("This script did not run Moneris payments.")
    print("This script did not change backend/auth/payment behavior.")
    print("This script did not unlock customer access.")
    print("This script did not activate paid SaaS production mode.")

    section("RESULT")
    if failures:
        print("PAID SAAS PRODUCTION READINESS MASTER PROOF: FAIL")
        print("Failures:")
        for failure in failures:
            print("-", failure)
        return 1

    print("PAID SAAS PRODUCTION READINESS MASTER PROOF: PASS")
    print("All expected local planning/proof/guard artifacts are present.")
    print("Paid SaaS production activation remains blocked until deployed-runtime blockers are actually completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
