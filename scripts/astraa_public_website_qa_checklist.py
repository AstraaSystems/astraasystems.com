#!/usr/bin/env python3
"""
Astraa Public Website QA Checklist

READ-ONLY SCRIPT.

Purpose:
- Define final marketing/public website QA before public visibility.
- Keep Workspace/customer tool access controlled.
- Separate marketing launch from paid SaaS launch.

Does NOT:
- modify files
- deploy Astraa
- open customer access
- change auth/payment/backend behavior
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
    section("ASTRAA PUBLIC WEBSITE QA CHECKLIST")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("PUBLIC WEBSITE LAUNCH GOAL")
    print("Launch Astraa as a professional, high-trust public marketing site while keeping customer tool access controlled.")

    section("VISUAL / BRAND QA")
    print_list([
        "Homepage feels clean, premium, calm, and not crowded.",
        "Brand colors stay within white, black, navy/royal blue.",
        "No neon/scammy/overly flashy styling.",
        "Estimator is highlighted as the primary product but other tools are still clearly represented.",
        "Mobile layout is readable and not cramped.",
        "Buttons, cards, pricing sections, and page spacing feel consistent.",
    ])

    section("PUBLIC LANGUAGE QA")
    print_list([
        "Use Tools, not Engines, in public-facing pages.",
        "Avoid public mention of internal names such as Arka, Lux, internal AI labels, or system architecture.",
        "Avoid unnecessary technical jargon.",
        "Astraa is positioned as a clean business software platform for businesses of many sizes.",
        "Copy should feel trustworthy, simple, and professional.",
    ])

    section("PAGE / LINK QA")
    print_list([
        "Homepage links work.",
        "Tools page and all tool subpages work.",
        "Pricing page works.",
        "Contact/trial flow works.",
        "Workspace login/register links work but remain controlled.",
        "Legal pages are reachable from footer.",
        "No broken navigation after deployment.",
    ])

    section("LEGAL / TRUST QA")
    print_list([
        "Privacy Policy present.",
        "Terms present.",
        "Payment/refund language present if payment is public.",
        "Contact information is clear.",
        "No overpromising about unsupported automation, integrations, or production readiness.",
    ])

    section("PAYMENT / WORKSPACE PUBLIC SAFETY")
    print_list([
        "Do not broadly open paid customer access yet.",
        "Do not expose dev-login publicly.",
        "Workspace access should remain controlled/internal/beta until production auth and managed DB are complete.",
        "Payment flows should remain in controlled QA unless final deployed Moneris regression is complete.",
    ])

    section("MARKETING LAUNCH DECISION")
    print("Marketing-only public launch: candidate after final visual/link/legal QA.")
    print("Paid SaaS launch: hold until production auth provider, managed DB, deployed secrets, and deployed Moneris regression are complete.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify files.")
    print("This script did not deploy Astraa.")
    print("This script did not open customer access.")
    print("This script did not change auth/payment/backend behavior.")


if __name__ == "__main__":
    main()
