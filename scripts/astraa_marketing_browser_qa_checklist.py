#!/usr/bin/env python3
"""
Astraa Marketing Browser QA Checklist

READ-ONLY SCRIPT.

Purpose:
- Provide final manual browser QA checklist before public marketing launch.
- Confirm public website visual, wording, pricing, and access-control readiness.

Does NOT:
- modify files
- deploy Astraa
- open customer access
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
    section("ASTRAA MARKETING BROWSER QA CHECKLIST")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("LOCAL SERVER COMMAND")
    print("python3 -m http.server 8080")

    section("PAGES TO REVIEW")
    print_list([
        "http://localhost:8080/index.html",
        "http://localhost:8080/tools.html",
        "http://localhost:8080/pricing.html",
        "http://localhost:8080/tool-finance.html",
        "http://localhost:8080/tool-operations.html",
        "http://localhost:8080/pricing-contractor.html",
        "http://localhost:8080/pricing-nonprofit.html",
        "http://localhost:8080/pricing-franchise.html",
        "http://localhost:8080/login.html",
        "http://localhost:8080/register.html",
        "http://localhost:8080/contact.html",
        "http://localhost:8080/terms.html",
    ])

    section("VISUAL QA")
    print_list([
        "Homepage is clean, premium, calm, and not crowded.",
        "White/black/navy/royal blue branding feels consistent.",
        "No neon/scammy/overly flashy styling.",
        "Cards, buttons, spacing, and sections feel balanced.",
        "Mobile layout does not break or feel cramped.",
    ])

    section("WORDING QA")
    print_list([
        "Public pages use Tools, not Engines.",
        "No internal names appear in public marketing/access pages.",
        "Copy avoids unnecessary technical jargon.",
        "Customer-facing claims are truthful and not overpromised.",
        "Workspace access is clearly controlled while production SaaS hardening continues.",
    ])

    section("PRICING QA")
    print_list([
        "Estimator Basic: $39.99 CAD/month.",
        "Estimator Professional: $99.99 CAD/month.",
        "Finance Basic: $29.99 CAD/month.",
        "Finance Professional: $79.99 CAD/month.",
        "Finance Personal: $24.99 CAD/month.",
        "Finance Non-Profit: $59.99 CAD/month.",
        "Operations Basic: $59.99 CAD/month.",
        "Operations Professional: $149.99 CAD/month.",
        "Operations Plus: $299.99 CAD/month.",
        "Contractor Professional: $279.99 CAD/month.",
    ])

    section("ACCESS SAFETY QA")
    print_list([
        "Login/register do not show internal product names.",
        "No dev-login link is exposed.",
        "No customer paid SaaS access is broadly opened.",
        "Contact/trial paths are controlled and appropriate for marketing launch.",
    ])

    section("FINAL DECISION")
    print("If all checks pass: Astraa is ready for marketing/public website visibility.")
    print("Paid SaaS launch remains blocked until production auth, managed DB, deployed secrets, host/TLS, and deployed Moneris regression are complete.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify files.")
    print("This script did not deploy Astraa.")
    print("This script did not open customer access.")
    print("This script did not change backend/auth/payment behavior.")


if __name__ == "__main__":
    main()
