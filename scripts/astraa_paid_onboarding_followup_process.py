#!/usr/bin/env python3
"""
Astraa Paid Onboarding Follow-Up Process

READ-ONLY SCRIPT.

Purpose:
- Define how Astraa should follow up with paid customer leads.
- Keep trial available while making paid onboarding the primary conversion path.
- Keep customer onboarding controlled until paid SaaS production blockers are complete.

Does NOT:
- send emails
- schedule meetings
- open customer access
- collect payment details
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
    section("ASTRAA PAID ONBOARDING FOLLOW-UP PROCESS")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("PRIMARY GOAL")
    print("Convert interested customers into paid onboarding or paid package discussions.")
    print("Trial remains available for evaluation, but paid onboarding is the primary path.")

    section("INTAKE SOURCES")
    print_list([
        "Astraa Support Concierge",
        "Request paid onboarding CTA",
        "Contact page",
        "Pricing page",
        "Trial request",
        "Direct relationship-based outreach replies",
    ])

    section("TRIAGE CATEGORIES")
    print_list([
        "PAID_READY — customer is asking about starting or buying.",
        "PACKAGE_GUIDANCE — customer needs help choosing plan/tool/package.",
        "TRIAL_EVALUATION — customer wants trial access before buying.",
        "CUSTOM_SETUP — contractor, franchise, non-profit, multi-location, or custom workflow.",
        "SUPPORT_GENERAL — general question, not yet commercial intent.",
    ])

    section("MINIMUM INFORMATION TO COLLECT")
    print_list([
        "Name",
        "Email",
        "Business or organization name",
        "Business type",
        "Tools interested in",
        "Current problem or workflow need",
        "Team size or users needed",
        "Preferred plan/package if known",
        "Contractor/franchise/non-profit/custom setup needs",
        "Preferred follow-up method",
        "Phone number only if customer requests a call",
    ])

    section("FOLLOW-UP FLOW")
    print_list([
        "Acknowledge the request.",
        "Confirm business type and need.",
        "Recommend the most relevant paid plan/package.",
        "Explain that trial is available but paid onboarding receives priority setup guidance.",
        "Offer three paths: paid onboarding, trial evaluation, or custom setup discussion.",
        "If paid-ready, move to controlled paid setup workflow.",
        "If trial-first, keep upgrade path clear.",
    ])

    section("PLAN RECOMMENDATION RULES")
    print_list([
        "Estimator Basic: small contractor/startup needing limited estimates.",
        "Estimator Professional: contractor/business needing more estimates and better value.",
        "Finance Basic: small business needing basic financial visibility.",
        "Finance Professional: growing business needing stronger financial control.",
        "Operations Professional: team needing scheduling, crew/subcontractor, and workflow coordination.",
        "Contractor Professional: Estimator Professional + Finance Professional + Operations Professional.",
        "Custom Suite: franchise, non-profit, contractor, multi-location, or special setup.",
    ])

    section("CONTROLLED ACCESS SAFETY")
    print_list([
        "Do not broadly auto-open paid SaaS access yet.",
        "Do not collect passwords or payment card details through email/chat.",
        "Do not promise instant production access.",
        "Do not import real customer data into production until production auth/DB/deployment are ready.",
        "Use controlled onboarding and support follow-up while paid SaaS blockers are completed.",
    ])

    section("CASL / CONSENT-SAFE MARKETING NOTE")
    print_list([
        "Use relationship-based or consent-based follow-up only.",
        "Commercial electronic messages must identify Astraa and include an unsubscribe path where applicable.",
        "Do not send bulk unsolicited commercial email/SMS.",
        "Keep proof of consent or customer inquiry where applicable.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not send emails.")
    print("This script did not schedule meetings.")
    print("This script did not open customer access.")
    print("This script did not collect payment details.")
    print("This script did not modify backend/auth/payment behavior.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
