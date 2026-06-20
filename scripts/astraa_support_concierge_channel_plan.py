#!/usr/bin/env python3
"""
Astraa Support Concierge Channel Plan

READ-ONLY SCRIPT.

Purpose:
- Define the support channel direction for Astraa.
- Clarify that V1 is a human/support connection box, not a bot.
- Prepare future live chat and digital phone support paths.

Does NOT:
- deploy Astraa
- buy phone numbers
- connect external providers
- send emails
- change backend/auth/payment behavior
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
    section("ASTRAA SUPPORT CONCIERGE CHANNEL PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("GOAL")
    print("Astraa should provide a support connection point, not a fake chatbot.")

    section("V1 — WEBSITE SUPPORT CONCIERGE")
    print_list([
        "Floating Ask Astraa support box on public pages.",
        "Clear wording: not a bot.",
        "Customers can ask questions, request onboarding help, or ask for pricing/package guidance.",
        "Requests open the visitor's email client with a prefilled message.",
        "Call request path is included.",
        "Digital phone number slot is prepared but not enabled until a provider/number is connected.",
    ])

    section("V2 — LIVE CHAT PROVIDER")
    print_list([
        "Connect a real live chat/helpdesk provider when ready.",
        "Good candidate path: tawk.to for free live chat/ticketing/knowledge base.",
        "Alternative: Intercom or similar if Astraa needs a larger customer support suite later.",
        "Only install third-party widget code after privacy/legal review.",
    ])

    section("V3 — DIGITAL PHONE / VOICE SUPPORT")
    print_list([
        "Connect a digital phone number after choosing provider.",
        "Candidate paths: Twilio Programmable Voice or Azure Communication Services.",
        "Voice support should help customers request onboarding, pricing guidance, and setup help.",
        "Do not imply 24/7 voice support until staffing/automation is actually ready.",
    ])

    section("SAFETY RULES")
    print_list([
        "Do not call it a bot.",
        "Do not claim instant human response unless true.",
        "Do not collect sensitive payment/password data through the chat box.",
        "Do not expose backend/internal routes.",
        "Do not open broad paid SaaS onboarding until production auth and managed DB are complete.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not deploy Astraa.")
    print("This script did not buy phone numbers.")
    print("This script did not connect external providers.")
    print("This script did not send emails.")
    print("This script did not change backend/auth/payment behavior.")


if __name__ == "__main__":
    main()
