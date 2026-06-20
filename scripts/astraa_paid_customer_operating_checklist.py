#!/usr/bin/env python3
"""
Astraa Paid Customer Operating Checklist

READ-ONLY SCRIPT.

Purpose:
- Provide a daily operating checklist for paid customer acquisition and onboarding follow-up.
- Help convert website/support leads into paid onboarding or package discussions.
- Keep trial available but secondary to paid onboarding.
- Keep real customer data local and out of git.

Does NOT:
- send emails
- create drafts
- schedule calls
- open customer access
- store customer data in git
- modify backend/auth/payment behavior
- deploy Astraa
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
    section("ASTRAA PAID CUSTOMER OPERATING CHECKLIST")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("DAILY INTAKE CHECK")
    print_list([
        "Check support@astraasystems.com for paid onboarding, trial, package, and support requests.",
        "Check any direct relationship-based replies or customer conversations.",
        "Add each serious lead to LOCAL_LEADS/astraa_paid_onboarding_leads.csv.",
        "Do not commit LOCAL_LEADS/ to git.",
    ])

    section("LEAD CLASSIFICATION")
    print_list([
        "PAID_READY — customer is asking about starting or buying.",
        "PACKAGE_GUIDANCE — customer needs help choosing tools or package.",
        "TRIAL_EVALUATION — customer wants to test before buying.",
        "CUSTOM_SETUP — contractor, franchise, non-profit, multi-location, or custom workflow.",
        "SUPPORT_GENERAL — question only, not commercial intent yet.",
    ])

    section("PLAN RECOMMENDATION")
    print_list([
        "Estimator Basic: small/startup contractor with limited estimate needs.",
        "Estimator Professional: contractor/business needing more estimates and better value.",
        "Finance Basic: small business needing financial visibility.",
        "Finance Professional: growing business needing stronger financial control.",
        "Operations Professional: team needing scheduling, coordination, crew/subcontractor workflow.",
        "Contractor Professional: Estimator Professional + Finance Professional + Operations Professional.",
        "Custom Suite: franchise, non-profit, contractor, multi-location, or special setup.",
    ])

    section("FOLLOW-UP ACTIONS")
    print_list([
        "If PAID_READY: send paid onboarding response and ask for setup details.",
        "If PACKAGE_GUIDANCE: recommend best plan/package and ask for business type/team size.",
        "If TRIAL_EVALUATION: explain trial is available but paid onboarding receives priority setup.",
        "If CUSTOM_SETUP: ask for organization structure, locations, users, and tool needs.",
        "If SUPPORT_GENERAL: answer clearly and guide to pricing/support if relevant.",
    ])

    section("SALES MESSAGE TO KEEP CONSISTENT")
    print("Trial access is available for evaluation, but paid onboarding receives priority setup and package guidance.")

    section("CONTROLLED ACCESS RULES")
    print_list([
        "Do not broadly auto-open paid SaaS access yet.",
        "Do not collect passwords or payment card details through chat/email.",
        "Do not promise instant production access.",
        "Do not import real customer data into production until production auth/DB/deployment are ready.",
        "Use controlled onboarding while paid SaaS blockers are completed.",
    ])

    section("LOCAL LEAD TRACKER STATUS VALUES")
    print_list([
        "NEW",
        "AWAITING_INFO",
        "PLAN_RECOMMENDED",
        "PAID_ONBOARDING_REQUESTED",
        "TRIAL_REQUESTED",
        "CUSTOM_SETUP_REVIEW",
        "CLOSED_NOT_READY",
        "DO_NOT_CONTACT",
    ])

    section("END-OF-DAY REVIEW")
    print_list([
        "Confirm every new lead has a triage_category.",
        "Confirm every commercial lead has a recommended_plan or next_action.",
        "Confirm no sensitive data was stored.",
        "Confirm no real customer lead data was committed to git.",
        "Confirm paid-ready leads have a clear next action.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not send emails.")
    print("This script did not create drafts.")
    print("This script did not schedule calls.")
    print("This script did not open customer access.")
    print("This script did not store customer data in git.")
    print("This script did not modify backend/auth/payment behavior.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
