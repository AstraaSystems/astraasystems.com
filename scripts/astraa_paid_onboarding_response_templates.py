#!/usr/bin/env python3
"""
Astraa Paid Onboarding Response Templates

READ-ONLY SCRIPT.

Purpose:
- Provide support email/message templates for paid onboarding follow-up.
- Keep wording paid-first but honest about controlled access.
- Avoid collecting sensitive payment/password details over email.

Does NOT:
- send emails
- create drafts
- schedule meetings
- open customer access
"""

from __future__ import annotations

from datetime import datetime, timezone


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def main():
    section("ASTRAA PAID ONBOARDING RESPONSE TEMPLATES")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("TEMPLATE 1 — PAID_READY")
    print("""
Subject: Astraa paid onboarding request

Hi [Name],

Thank you for reaching out to Astraa.

Based on what you shared, the best next step is to confirm the tool or package that fits your business and prepare a controlled paid onboarding path.

To help recommend the right setup, please reply with:
- Business or organization name
- Tools you are interested in
- Team size or number of users
- Whether you need contractor, franchise, non-profit, or custom setup
- Preferred follow-up method

Trial access is available for evaluation, but paid onboarding receives priority setup and package guidance.

Please do not send passwords or payment card details by email.

Astraa Support
""".strip())

    section("TEMPLATE 2 — PACKAGE_GUIDANCE")
    print("""
Subject: Astraa package guidance

Hi [Name],

Thanks for asking about Astraa.

Astraa can be started with individual tools or bundled packages. The usual starting points are:
- Estimator for estimating and project pricing
- Finance for financial visibility and payment tracking
- Operations for scheduling, team coordination, and workflow visibility
- Contractor Professional for Estimator + Finance + Operations
- Custom Suite for franchise, non-profit, multi-location, or special setup needs

If you send your business type, team size, and main workflow problem, we can recommend the best paid plan or package.

Astraa Support
""".strip())

    section("TEMPLATE 3 — TRIAL_EVALUATION")
    print("""
Subject: Astraa trial and paid onboarding options

Hi [Name],

Thank you for your interest in Astraa.

Trial access is available for evaluation. If your goal is to start using Astraa for business operations, paid onboarding is the recommended path because it gives clearer plan selection and setup guidance.

Please reply with:
- Which tool you want to evaluate
- Your business type
- Whether you are considering Basic, Professional, or a package
- Any setup questions before starting

Astraa Support
""".strip())

    section("TEMPLATE 4 — CUSTOM_SETUP")
    print("""
Subject: Astraa custom setup request

Hi [Name],

Thanks for reaching out about a custom Astraa setup.

Custom setup is the right path when a business needs contractor access, franchise or multi-location structure, non-profit pricing, multiple tools, or special workflow requirements.

Please reply with:
- Organization type
- Number of users or teams
- Locations or divisions, if applicable
- Tools needed
- Any contractor, franchise, non-profit, or custom workflow requirements
- Preferred follow-up method

Astraa Support
""".strip())

    section("READ-ONLY CONFIRMATION")
    print("This script did not send emails.")
    print("This script did not create drafts.")
    print("This script did not schedule meetings.")
    print("This script did not open customer access.")


if __name__ == "__main__":
    main()
