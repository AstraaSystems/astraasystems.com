#!/usr/bin/env python3
"""
Astraa Managed DB Requirements

READ-ONLY SCRIPT.

Purpose:
- Define staging vs production managed DB requirements.
- Keep requirements aligned with Astraa's current local staging DB proof and future SaaS launch.

Does NOT:
- connect to a database
- create databases
- migrate data
- modify files
- patch storage behavior
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
    section("ASTRAA MANAGED DB REQUIREMENTS")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("STAGING DB REQUIREMENTS")
    print_list([
        "Separate from production DB.",
        "Can receive reviewed KEEP_AS_PROOF records first.",
        "Can receive selected manually reviewed records later.",
        "Must support schema/index structure proven by local SQLite staging.",
        "Must support repeatable idempotent import tests.",
        "Must allow safe reset/rebuild during staging validation.",
        "Must not contain broad real customer data until production auth and deployment are proven.",
    ])

    section("PRODUCTION DB REQUIREMENTS")
    print_list([
        "Separate from staging DB.",
        "Backups and restore process required.",
        "TLS/secure connection required.",
        "Credentials stored outside git.",
        "Least-privilege DB user for application runtime.",
        "Audit-friendly structure for payments, payment_events, usage counters, accounts, subscriptions, Core OS activity, and event logs.",
        "Migration/cutover must be repeatable and reviewed.",
        "No unreviewed QA/archive/malicious test data should be imported.",
    ])

    section("REQUIRED TABLE GROUPS")
    print_list([
        "accounts",
        "subscriptions",
        "usage_counters",
        "payments",
        "payment_events",
        "core_entities",
        "core_activity",
        "core_events",
        "core_vault_records",
        "event_logs",
    ])

    section("REQUIRED SAFETY CLASSIFICATIONS")
    print_list([
        "KEEP_AS_PROOF — eligible for first staging import.",
        "ARCHIVE_LATER — exclude from staging/production import by default.",
        "DO_NOT_MIGRATE — never import.",
        "MANUAL_REVIEW — import only after explicit review.",
    ])

    section("REQUIRED PROOFS BEFORE PRODUCTION DB CUTOVER")
    print_list([
        "Local staging DB proof passes.",
        "Managed staging schema created and validated.",
        "Managed staging import dry-run reviewed.",
        "Managed staging guarded import passes.",
        "Source-vs-managed-staging reconciliation passes.",
        "Post-auth-hardening proof passes.",
        "CORS hardening proof passes.",
        "Gunicorn smoke test passes.",
        "Payment/preload regression passes against deployed/staging API.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not connect to a database.")
    print("This script did not create databases.")
    print("This script did not migrate data.")
    print("This script did not modify files.")


if __name__ == "__main__":
    main()
