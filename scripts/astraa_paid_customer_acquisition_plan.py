#!/usr/bin/env python3
"""
Astraa Paid Customer Acquisition Plan

READ-ONLY SCRIPT.

Purpose:
- Shift Astraa from trial-only interest to paid-first customer acquisition.
- Keep trial available but position paid plans and controlled onboarding as the primary path.
- Preserve paid SaaS safety boundaries while production auth/DB/deployment are pending.

Does NOT:
- send emails
- post to social media
- open broad customer access
- change backend/auth/payment behavior
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
    section("ASTRAA PAID CUSTOMER ACQUISITION PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("PRIMARY SALES POSITION")
    print("Astraa is available through paid plans and controlled onboarding requests.")
    print("Trial access is available for evaluation, but paid customers receive priority setup and support.")

    section("CUSTOMER PATHS")
    print_list([
        "Paid plan request: customer chooses a plan/package and asks for setup.",
        "Paid onboarding request: customer asks Astraa to help choose tools and start correctly.",
        "Trial request: customer evaluates selected functionality before committing.",
        "Custom package request: contractor, franchise, non-profit, or multi-location setup.",
    ])

    section("WEBSITE CTA PRIORITY")
    print_list([
        "Primary CTA: Request Paid Onboarding.",
        "Secondary CTA: View Pricing.",
        "Tertiary CTA: Ask Astraa / Trial Access.",
    ])

    section("WHAT TO SELL FIRST")
    print_list([
        "Estimator Basic or Professional for contractors needing estimates.",
        "Finance Basic or Professional for businesses needing financial visibility.",
        "Operations Professional for teams needing scheduling/coordination.",
        "Contractor Professional bundle for Estimator + Finance + Operations.",
        "Custom Suite for franchise, non-profit, contractor, or multi-location needs.",
    ])

    section("SAFETY BOUNDARY")
    print_list([
        "Do not broadly open automated paid SaaS onboarding yet.",
        "Use controlled onboarding and support follow-up while production auth/DB/deployment are completed.",
        "Do not overpromise instant setup or full production automation.",
        "Do not send unsolicited bulk commercial email/SMS.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not send emails.")
    print("This script did not post to social media.")
    print("This script did not open broad customer access.")
    print("This script did not change backend/auth/payment behavior.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
