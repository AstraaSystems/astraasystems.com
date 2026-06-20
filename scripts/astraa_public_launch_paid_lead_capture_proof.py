#!/usr/bin/env python3
"""
Astraa Public Launch + Paid Lead Capture Proof

DEFAULT-SAFE SCRIPT.

Purpose:
- Prove Astraa is ready for marketing/public website visibility and manual paid lead capture.
- Confirm paid onboarding follow-up process exists.
- Confirm local lead tracker is protected from git.
- Confirm broad automated paid SaaS onboarding remains blocked until production auth, managed DB,
  secure deployed secrets, host/TLS, and deployed Moneris regression are complete.

Does NOT:
- send emails
- create drafts
- schedule calls
- open customer access
- store real customer data
- deploy Astraa
- modify backend/auth/payment behavior
- run Moneris payments
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ("Marketing enablement proof", [sys.executable, "scripts/astraa_marketing_enablement_proof.py"]),
    ("Final marketing launch decision pack", [sys.executable, "scripts/astraa_final_marketing_launch_decision_pack.py"]),
    ("Marketing browser QA checklist", [sys.executable, "scripts/astraa_marketing_browser_qa_checklist.py"]),
    ("Public website file inventory", [sys.executable, "scripts/astraa_public_website_file_inventory.py"]),
    ("Public website risk classifier", [sys.executable, "scripts/astraa_public_website_risk_classifier.py"]),
    ("Pricing card layout QA", [sys.executable, "scripts/astraa_pricing_card_layout_qa.py"]),
    ("Paid customer acquisition plan", [sys.executable, "scripts/astraa_paid_customer_acquisition_plan.py"]),
    ("Paid onboarding follow-up proof", [sys.executable, "scripts/astraa_paid_onboarding_followup_proof.py"]),
    ("Paid customer operating checklist", [sys.executable, "scripts/astraa_paid_customer_operating_checklist.py"]),
    ("Paid SaaS implementation lane", [sys.executable, "scripts/astraa_paid_saas_implementation_lane.py"]),
    ("Paid SaaS blocker execution plan", [sys.executable, "scripts/astraa_paid_saas_blocker_execution_plan.py"]),
    ("Production auth provider selection decision", [sys.executable, "scripts/astraa_production_auth_provider_selection_decision.py"]),
    ("Local paid lead tracker creator", [sys.executable, "scripts/astraa_create_local_paid_lead_tracker.py"]),
    ("Local lead tracker gitignore check", ["git", "check-ignore", "-v", "LOCAL_LEADS/astraa_paid_onboarding_leads.csv"]),
    ("Git status", ["git", "status", "-sb"]),
    ("Git log", ["git", "log", "--oneline", "-n", "14"]),
]


def section(title: str):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def run(name: str, cmd: list[str]) -> int:
    section(name)
    print("Command:", " ".join(cmd))

    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    if proc.stdout:
        print(proc.stdout.rstrip())

    if proc.stderr:
        print("\nSTDERR:")
        print(proc.stderr.rstrip())

    print("\nExit code:", proc.returncode)
    return proc.returncode


def main():
    section("ASTRAA PUBLIC LAUNCH + PAID LEAD CAPTURE PROOF")
    print("Mode: DEFAULT-SAFE")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", ROOT)

    results = {}

    for name, cmd in COMMANDS:
        results[name] = run(name, cmd)

    section("PUBLIC LAUNCH + PAID LEAD CAPTURE SUMMARY")

    all_ok = True

    for name, code in results.items():
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status}: {name} ({code})")
        if code != 0:
            all_ok = False

    print("")

    if all_ok:
        print("✅ ASTRAA PUBLIC LAUNCH + PAID LEAD CAPTURE PROOF PASSED")
        print("Marketing/public website visibility can proceed after human browser visual review.")
        print("Paid lead capture and manual paid onboarding follow-up are ready to operate.")
        print("Broad automated paid SaaS onboarding remains blocked until production auth, managed DB, secure deployed secrets, host/TLS, and deployed Moneris regression are complete.")
    else:
        print("❌ ASTRAA PUBLIC LAUNCH + PAID LEAD CAPTURE PROOF FAILED")
        print("Review failed sections above before driving traffic or capturing paid leads.")

    section("GO CONDITIONS CONFIRMED IF PASSED")
    print("- Public website marketing foundation exists.")
    print("- Pricing, Support, Contact, Tools, Login, and Register pages are covered by QA scripts.")
    print("- Paid-first CTAs exist.")
    print("- Support Concierge exists.")
    print("- Paid onboarding follow-up process exists.")
    print("- Local paid lead tracker exists and is ignored by git.")
    print("- Paid SaaS automation blockers remain documented.")

    section("NO-GO CONDITIONS THAT REMAIN")
    print("- Do not broadly auto-open paid SaaS customer access yet.")
    print("- Do not import real customer data into production yet.")
    print("- Do not collect passwords or payment card details by email/chat.")
    print("- Do not claim fully automated paid SaaS onboarding is ready.")
    print("- Do not run live deployed payment onboarding until deployed Moneris regression passes.")

    section("SAFETY CONFIRMATION")
    print("This script did not send emails.")
    print("This script did not create drafts.")
    print("This script did not schedule calls.")
    print("This script did not open customer access.")
    print("This script did not store real customer data.")
    print("This script did not deploy Astraa.")
    print("This script did not modify backend/auth/payment behavior.")
    print("This script did not run Moneris payments.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
