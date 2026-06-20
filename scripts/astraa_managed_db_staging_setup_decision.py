#!/usr/bin/env python3
"""
Astraa Managed DB Staging Setup Decision

READ-ONLY SCRIPT.

Purpose:
- Convert managed DB planning into a staging setup decision path.
- Keep no DB connection/no migration/no patch.

Does NOT:
- connect to a database
- create databases
- migrate data
- modify api.py
- patch storage wrappers
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
    section("ASTRAA MANAGED DB STAGING SETUP DECISION")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("CURRENT DB STATE")
    print_list([
        "JSON/JSONL source-of-truth works for internal QA.",
        "Local SQLite staging proof exists.",
        "KEEP_AS_PROOF rows imported and reconciled locally.",
        "Managed DB provider has not been chosen.",
        "No managed DB connection exists yet.",
    ])

    section("RECOMMENDED DB DIRECTION")
    print_list([
        "Use managed PostgreSQL-compatible database as default serious candidate.",
        "Create separate managed staging DB before production DB.",
        "Do not connect runtime api.py to managed DB until adapter/tests exist.",
        "Keep local SQLite proof as bridge and fallback proof.",
    ])

    section("MANAGED STAGING SETUP REQUIREMENTS")
    print_list([
        "Separate staging database from production.",
        "TLS/secure connection available.",
        "Credentials stored outside git.",
        "Least-privilege app user.",
        "Schema/indexes based on existing staging schema/index plan.",
        "Safe reset/rebuild possible during staging testing.",
        "No broad customer data imported at this stage.",
    ])

    section("FIRST MANAGED STAGING IMPORT POLICY")
    print_list([
        "Import KEEP_AS_PROOF only first.",
        "Exclude ARCHIVE_LATER by default.",
        "Exclude DO_NOT_MIGRATE always.",
        "Require explicit review for MANUAL_REVIEW.",
        "Run source-vs-managed-staging reconciliation after import.",
    ])

    section("CUTOVER DECISION RULE")
    print_list([
        "Do not cut runtime storage to managed DB until managed staging proofs pass.",
        "Do not create production DB import until staging DB import/reconcile/proofs pass.",
        "Do not open paid customer access until production auth and managed DB are both proven.",
    ])

    section("NEXT TECHNICAL STEP AFTER PROVIDER CHOICE")
    print_list([
        "Create managed staging DB externally/securely.",
        "Store staging DATABASE_URL securely outside git.",
        "Create managed DB schema validation script.",
        "Create managed DB connection self-test script that refuses without explicit flag.",
        "Create managed staging import dry-run before any real import.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not connect to a database.")
    print("This script did not create databases.")
    print("This script did not migrate data.")
    print("This script did not modify api.py.")
    print("This script did not patch storage wrappers.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
