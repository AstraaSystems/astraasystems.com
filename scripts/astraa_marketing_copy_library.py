#!/usr/bin/env python3
"""
Astraa Marketing Copy Library

READ-ONLY SCRIPT.

Purpose:
- Provide launch-safe marketing copy for manual website/social/outreach use.
- Keep public wording clean and professional.
- Avoid unsupported claims and internal names.

Does NOT:
- send emails
- post to social media
- buy ads
- scrape contacts
- deploy Astraa
"""

from __future__ import annotations

from datetime import datetime, timezone


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def main():
    section("ASTRAA MARKETING COPY LIBRARY")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("CORE POSITIONING")
    print("Astraa Systems helps businesses organize estimating, finance, operations, and workspace workflows through clean modular tools.")

    section("SHORT WEBSITE TAGLINES")
    print("- Business tools that help teams work with clarity.")
    print("- Estimating, finance, and operations — organized in one calm workspace.")
    print("- Practical software for businesses that want less friction and better control.")

    section("LINKEDIN / SOCIAL POST DRAFTS")
    print("""
Post 1:
Astraa Systems is being built to help businesses simplify estimating, finance, operations, and workspace access through clean modular tools.

The goal is simple: practical software that helps small and growing teams operate with more clarity.

Public website QA is underway, with customer access remaining controlled while production auth and managed database work continue.
""".strip())

    print("\n---\n")

    print("""
Post 2:
We have added launch pricing paths for Astraa Estimator, Finance, and Operations.

Astraa is designed as a modular business platform, so teams can start with one tool and grow into packages as their needs expand.

Marketing site readiness is moving forward while paid customer access remains controlled until the production backend is fully ready.
""".strip())

    section("CONSENT-SAFE OUTREACH NOTE")
    print("""
For direct outreach, use personal relationship-based messages only where appropriate.
Do not send bulk commercial email or SMS without consent, identification, and unsubscribe handling.
""".strip())

    section("READ-ONLY CONFIRMATION")
    print("This script did not send emails.")
    print("This script did not post to social media.")
    print("This script did not buy ads.")
    print("This script did not scrape contacts.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
