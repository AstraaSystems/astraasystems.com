#!/usr/bin/env python3
"""
Astraa Local Paid Lead Tracker Creator

LOCAL-ONLY UTILITY.

Purpose:
- Create a local paid onboarding lead tracker CSV under LOCAL_LEADS/.
- Keep real customer lead data out of git.
- Support manual paid onboarding follow-up.

Does NOT:
- send emails
- store data in backend
- open customer access
- modify auth/payment behavior
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import csv


ROOT = Path(__file__).resolve().parents[1]
LEADS_DIR = ROOT / "LOCAL_LEADS"
TRACKER = LEADS_DIR / "astraa_paid_onboarding_leads.csv"

FIELDS = [
    "lead_id",
    "received_source",
    "received_date",
    "name",
    "email",
    "business_name",
    "business_type",
    "triage_category",
    "tools_interested",
    "recommended_plan",
    "team_size",
    "custom_setup_needed",
    "followup_status",
    "next_action",
    "notes_no_sensitive_data",
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def main():
    section("ASTRAA LOCAL PAID LEAD TRACKER CREATOR")
    print("Mode: LOCAL FILE CREATE")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    LEADS_DIR.mkdir(exist_ok=True)

    if TRACKER.exists():
        print("Tracker already exists:", TRACKER)
        print("No changes made.")
    else:
        with TRACKER.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)

        print("Created tracker:", TRACKER)

    section("SAFETY RULES")
    print("Do not store passwords.")
    print("Do not store payment card details.")
    print("Do not commit LOCAL_LEADS/ to git.")
    print("Use notes_no_sensitive_data for business context only.")

    section("NEXT MANUAL WORKFLOW")
    print("1. Add each paid onboarding request as a row.")
    print("2. Classify triage_category.")
    print("3. Recommend plan/package.")
    print("4. Set followup_status.")
    print("5. Use response templates from scripts/astraa_paid_onboarding_response_templates.py.")

    section("LOCAL-ONLY CONFIRMATION")
    print("This script did not send emails.")
    print("This script did not open customer access.")
    print("This script did not modify backend/auth/payment behavior.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
