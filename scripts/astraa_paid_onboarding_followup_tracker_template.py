#!/usr/bin/env python3
"""
Astraa Paid Onboarding Follow-Up Tracker Template

READ-ONLY SCRIPT.

Purpose:
- Print a safe template for manually tracking paid onboarding leads.
- Avoid storing real customer data in git by default.

Does NOT:
- create customer records
- store customer data
- send messages
- modify backend/auth/payment behavior
"""

from __future__ import annotations

from datetime import datetime, timezone


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
    section("ASTRAA PAID ONBOARDING FOLLOW-UP TRACKER TEMPLATE")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("SAFE TRACKER FIELDS")
    for field in FIELDS:
        print(field)

    section("STATUS VALUES")
    for status in [
        "NEW",
        "AWAITING_INFO",
        "PLAN_RECOMMENDED",
        "PAID_ONBOARDING_REQUESTED",
        "TRIAL_REQUESTED",
        "CUSTOM_SETUP_REVIEW",
        "CLOSED_NOT_READY",
        "DO_NOT_CONTACT",
    ]:
        print(status)

    section("SAFETY RULES")
    print("Do not store passwords.")
    print("Do not store payment card details.")
    print("Do not commit real customer lead data to git.")
    print("Use this as a template only.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not create customer records.")
    print("This script did not store customer data.")
    print("This script did not send messages.")
    print("This script did not modify backend/auth/payment behavior.")


if __name__ == "__main__":
    main()
