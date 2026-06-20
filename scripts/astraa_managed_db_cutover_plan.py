#!/usr/bin/env python3
"""
Astraa Managed DB Cutover Plan

READ-ONLY SCRIPT.

Purpose:
- Define migration/cutover sequence from JSON/local SQLite proof to managed DB.
- Preserve current storage wrappers and proof scripts.
- Keep no DB connection/no migration/no patch.

Does NOT:
- connect to a database
- create databases
- migrate data
- modify api.py
- modify storage wrappers
- patch runtime behavior
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
    section("ASTRAA MANAGED DB CUTOVER PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("CUTOVER PRINCIPLE")
    print_list([
        "Do not jump directly from JSON files to production DB.",
        "Use local SQLite proof as bridge.",
        "Then use managed staging DB.",
        "Then use production DB only after staging validation and deployed regression.",
        "Storage wrappers should make DB backend swap possible without rewriting route logic.",
    ])

    section("PHASE 0 — CURRENT COMPLETE STATE")
    print_list([
        "JSON/JSONL runtime proof exists.",
        "Storage abstraction wrappers exist.",
        "Local SQLite staging proof exists.",
        "KEEP_AS_PROOF import/reconcile/proof exists.",
        "No managed DB connection exists yet.",
    ])

    section("PHASE 1 — MANAGED STAGING DB ONLY")
    print_list([
        "Choose managed DB provider.",
        "Create managed staging DB manually/securely outside app runtime.",
        "Store staging DATABASE_URL securely outside git.",
        "Create managed staging schema using reviewed schema/index plan.",
        "Do not point api.py runtime to managed staging yet.",
        "Run dry-run import preview first.",
    ])

    section("PHASE 2 — GUARDED MANAGED STAGING IMPORT")
    print_list([
        "Import KEEP_AS_PROOF only first.",
        "Exclude ARCHIVE_LATER, DO_NOT_MIGRATE, MANUAL_REVIEW by default.",
        "Use idempotent import behavior.",
        "Run row inspector.",
        "Run source-vs-managed-staging reconciliation.",
        "Run post-auth/CORS/Gunicorn/staging proofs.",
    ])

    section("PHASE 3 — STORAGE BACKEND ADAPTER")
    print_list([
        "Add managed DB adapter behind storage abstraction wrappers.",
        "Keep JSON backend default until managed staging is proven.",
        "Use explicit ASTRAA_STORAGE_BACKEND=managed_db or similar only after tests exist.",
        "Do not remove JSON backend until production DB path is proven and backed up.",
    ])

    section("PHASE 4 — PRODUCTION DB PREP")
    print_list([
        "Create separate production DB.",
        "Set least-privilege app DB user.",
        "Enable backups/restore process.",
        "Store production DB credentials in secure environment/secret manager.",
        "Run schema validation against production DB before any import.",
        "Do not import test/proof data into production unless intentionally retained as internal proof in separate namespace.",
    ])

    section("PHASE 5 — FINAL CUTOVER")
    print_list([
        "Deploy app with production auth provider/session.",
        "Deploy app with managed DB backend selected.",
        "Run /health through deployed API.",
        "Run CORS hardening proof against deployed origin where possible.",
        "Run Moneris preload live regression.",
        "Run approved-payment verification/idempotency regression.",
        "Only then consider opening real customer access.",
    ])

    section("ROLLBACK PLAN")
    print_list([
        "Keep JSON/local staging proof untouched.",
        "Keep storage backend env switch reversible.",
        "If managed DB adapter fails, revert ASTRAA_STORAGE_BACKEND to json.",
        "Do not delete local proof data during initial managed DB cutover.",
        "Use git revert for code-level adapter/patch rollback.",
    ])

    section("READ-ONLY CONFIRMATION")
    print("This script did not connect to a database.")
    print("This script did not create databases.")
    print("This script did not migrate data.")
    print("This script did not modify api.py.")
    print("This script did not patch runtime behavior.")


if __name__ == "__main__":
    main()
