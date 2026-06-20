#!/usr/bin/env python3
"""
Astraa Finance + Operations Pricing Decision

READ-ONLY SCRIPT.

Purpose:
- Lock recommended launch pricing for Astraa Finance and Astraa Operations.
- Provide pricing guidance for public website pricing pages and package pages.
- Keep pricing separate from backend enforcement until intentionally implemented.

Does NOT:
- modify website files
- modify backend payment enforcement
- change Moneris logic
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
    section("ASTRAA FINANCE + OPERATIONS PRICING DECISION")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Currency: CAD")

    section("ASTRAA FINANCE PRICING")
    print_list([
        "Finance Basic: $29.99 CAD/month — single user, small/startup businesses.",
        "Finance Professional: $79.99 CAD/month — includes up to 3 users, growing businesses.",
        "Finance Personal: $24.99 CAD/month — personal/non-business finance users.",
        "Finance Non-Profit: $59.99 CAD/month — standard package between Basic and Professional.",
        "Finance Custom: custom quote — franchises, contractors, multi-location, special reporting, custom workflows.",
    ])

    section("ASTRAA OPERATIONS PRICING")
    print_list([
        "Operations Basic: $59.99 CAD/month — single user, basic scheduling and job coordination.",
        "Operations Professional: $149.99 CAD/month — includes up to 5 users, crews/subcontractors/certifications/field updates.",
        "Operations Plus: $299.99 CAD/month — includes up to 10 users, multi-location/staging/SLA/field check-in workflows.",
        "Operations Custom: custom quote — contractors, franchises, non-profits, multi-company setups, high-volume teams.",
    ])

    section("BUNDLE PRICING")
    print_list([
        "Business Starter: Estimator Basic + Finance Basic — $59.99 CAD/month.",
        "Business Professional: Estimator Professional + Finance Professional — $159.99 CAD/month.",
        "Operations Bundle: Finance Professional + Operations Professional — $199.99 CAD/month.",
        "Contractor Professional: Estimator Professional + Finance Professional + Operations Professional — $279.99 CAD/month.",
        "Custom Suite: any selected tools/users/contractors/franchise setup — custom quote.",
    ])

    section("PUBLIC WEBSITE NOTES")
    print_list([
        "Use 'Tools', not 'Engines'.",
        "Avoid internal system names on public pricing pages.",
        "Show Finance as simpler and lower-cost than Operations.",
        "Show Operations as team/field/workflow coordination, priced higher due to operational complexity.",
        "Keep paid customer access controlled until production auth and managed DB are complete.",
        "Pricing can be shown as launch pricing and adjusted later after customer validation.",
    ])

    section("BACKEND IMPLEMENTATION NOTES")
    print_list([
        "Do not patch Moneris/payment enforcement yet.",
        "Do not add these prices to backend purchase_type enforcement until public pricing page is reviewed.",
        "Keep Estimator current pricing unchanged: Basic $39.99/month, Professional $99.99/month.",
        "When implementing backend payments later, add explicit purchase_type values for finance_basic, finance_professional, operations_basic, operations_professional, operations_plus, and bundles.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify website files.")
    print("This script did not modify backend payment enforcement.")
    print("This script did not change Moneris logic.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
