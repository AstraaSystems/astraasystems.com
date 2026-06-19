#!/usr/bin/env python3
"""
Astraa DB Migration Dry Run

READ-ONLY SCRIPT.
Builds a proposed migration map from local JSON/JSONL stores to future managed DB tables.

Does NOT:
- write to a database
- modify local files
- delete local files
- archive files
- repair records
- migrate data

Purpose:
- Preview what local data would become in a managed DB.
- Separate proof/test/archive/do-not-migrate records before real migration work.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict


ROOT = Path(".")
USAGE_DB = ROOT / "astraa_data" / "astraa_usage_db.json"
PAYMENT_DB = ROOT / "astraa_data" / "astraa_payment_db.json"
SESSIONS_DB = ROOT / "astraa_data" / "astraa_sessions.json"
CORE_OS_DB = ROOT / "astraa_data" / "astraa_core_os_store.json"
PRELOADS_JSONL = ROOT / "preloads.jsonl"
PAYMENTS_JSONL = ROOT / "payments.jsonl"
RECEIPTS_JSONL = ROOT / "receipts.jsonl"
LEADS_JSONL = ROOT / "leads.jsonl"


KNOWN_PROOF_EMAILS = {
    "approved.live.test@astraasystems.com",
    "astraa.live.test@astraasystems.com",
}

DO_NOT_MIGRATE_MARKERS = [
    "malicious-change",
    "_TICKET_HERE",
    "TICKET_HERE",
    "bad_purchase_type",
]


def load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        print(f"⚠️ Could not parse {path}: {exc}")
        return fallback


def load_jsonl(path: Path):
    if not path.exists():
        return []

    rows = []
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            row["_source_line"] = idx
            rows.append(row)
        except Exception as exc:
            rows.append({
                "_parse_error": str(exc),
                "_line_number": idx,
                "_raw": line[:500],
            })
    return rows


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def is_test_email(email):
    email_l = str(email or "").lower()
    return any(marker in email_l for marker in ["test", "qa", "keshanth.sivayo@gmail.com"])


def should_not_migrate_record(record):
    raw = json.dumps(record, sort_keys=True, default=str).lower()
    return any(marker.lower() in raw for marker in DO_NOT_MIGRATE_MARKERS)


def classify_account(email, record):
    email_l = str(email or "").lower()

    if "malicious-change" in email_l:
        return "DO_NOT_MIGRATE"

    if email_l in KNOWN_PROOF_EMAILS and record.get("payment_status") == "active":
        return "KEEP_AS_PROOF"

    if is_test_email(email):
        return "ARCHIVE_LATER"

    return "MANUAL_REVIEW"


def classify_payment(record):
    if should_not_migrate_record(record):
        return "DO_NOT_MIGRATE"

    email_l = str(record.get("account_email") or "").lower()
    if email_l in KNOWN_PROOF_EMAILS and record.get("verified") is True and record.get("receipt_approved") is True:
        return "KEEP_AS_PROOF"

    if is_test_email(email_l):
        return "ARCHIVE_LATER"

    return "MANUAL_REVIEW"


def proposed_accounts_and_usage(usage_db):
    accounts = []
    subscriptions = []
    usage_counters = []

    for email, record in usage_db.items():
        classification = classify_account(email, record)

        account = {
            "migration_classification": classification,
            "account_id": record.get("account_id") or email,
            "primary_email": email,
            "status": record.get("payment_status"),
            "source": "astraa_usage_db.json",
        }

        subscription = {
            "migration_classification": classification,
            "account_id": record.get("account_id") or email,
            "selected_tool": record.get("selected_tool") or "Astraa Estimator",
            "selected_plan": record.get("selected_plan") or record.get("plan"),
            "payment_status": record.get("payment_status"),
            "subscription_status": record.get("subscription_status"),
            "billing_period_key": record.get("billing_period_key"),
            "source": "astraa_usage_db.json",
        }

        usage = {
            "migration_classification": classification,
            "account_id": record.get("account_id") or email,
            "selected_tool": record.get("selected_tool") or "Astraa Estimator",
            "billing_period_key": record.get("billing_period_key"),
            "estimate_limit": record.get("estimate_limit"),
            "estimate_used": record.get("estimate_used"),
            "extra_estimate_credits_total": record.get("extra_estimate_credits_total"),
            "extra_estimate_credits_used": record.get("extra_estimate_credits_used"),
            "source": "astraa_usage_db.json",
        }

        accounts.append(account)
        subscriptions.append(subscription)
        usage_counters.append(usage)

    return accounts, subscriptions, usage_counters


def proposed_payments(payment_db):
    payments = []
    payment_events = []

    for record in payment_db:
        classification = classify_payment(record)

        payments.append({
            "migration_classification": classification,
            "payment_id": record.get("payment_id"),
            "account_email": record.get("account_email"),
            "purchase_type": record.get("purchase_type"),
            "verified": record.get("verified"),
            "receipt_approved": record.get("receipt_approved"),
            "verification_source": record.get("verification_source"),
            "created_at": record.get("created_at"),
            "source": "astraa_payment_db.json",
        })

        payment_events.append({
            "migration_classification": classification,
            "payment_id": record.get("payment_id"),
            "event_type": "payment_verification_record",
            "event_status": "verified" if record.get("verified") else "not_verified",
            "event_reason": record.get("verification_reason"),
            "safe_gateway_reference": record.get("ticket_reference"),
            "source": "astraa_payment_db.json",
        })

    return payments, payment_events


def proposed_core(core_db):
    if not isinstance(core_db, dict):
        core_db = {}

    return {
        "core_entities": core_db.get("entities", []),
        "core_activity": core_db.get("activity", []),
        "core_events": core_db.get("events", []),
        "core_vault_records": core_db.get("vaultRecords", []),
    }


def proposed_event_logs():
    event_logs = []

    sources = [
        ("preloads", PRELOADS_JSONL),
        ("payments_jsonl", PAYMENTS_JSONL),
        ("receipts", RECEIPTS_JSONL),
        ("leads", LEADS_JSONL),
    ]

    for log_name, path in sources:
        for row in load_jsonl(path):
            event_logs.append({
                "migration_classification": "ARCHIVE_LATER" if is_test_email(row.get("email")) else "MANUAL_REVIEW",
                "log_name": log_name,
                "source_file": str(path),
                "source_line": row.get("_source_line") or row.get("_line_number"),
                "status": row.get("status"),
                "email": row.get("email"),
                "timestamp": row.get("timestamp"),
            })

    return event_logs


def print_table_summary(name, rows, sample_limit=3):
    section(name)

    print("Proposed row count:", len(rows))

    classifications = Counter(row.get("migration_classification", "UNCLASSIFIED") for row in rows if isinstance(row, dict))
    if classifications:
        print("Classification counts:")
        for key, value in classifications.most_common():
            print(f"  {key}: {value}")

    print("\nSample rows:")
    for row in rows[:sample_limit]:
        print(json.dumps(row, indent=2, sort_keys=True))


def main():
    section("ASTRAA DB MIGRATION DRY RUN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", Path.cwd())

    usage_db = load_json(USAGE_DB, {})
    payment_db = load_json(PAYMENT_DB, [])
    core_db = load_json(CORE_OS_DB, {})

    accounts, subscriptions, usage_counters = proposed_accounts_and_usage(usage_db)
    payments, payment_events = proposed_payments(payment_db)
    core = proposed_core(core_db)
    event_logs = proposed_event_logs()

    print_table_summary("PROPOSED TABLE: accounts", accounts)
    print_table_summary("PROPOSED TABLE: subscriptions", subscriptions)
    print_table_summary("PROPOSED TABLE: usage_counters", usage_counters)
    print_table_summary("PROPOSED TABLE: payments", payments)
    print_table_summary("PROPOSED TABLE: payment_events", payment_events)
    print_table_summary("PROPOSED TABLE: core_entities", core["core_entities"])
    print_table_summary("PROPOSED TABLE: core_activity", core["core_activity"])
    print_table_summary("PROPOSED TABLE: core_events", core["core_events"])
    print_table_summary("PROPOSED TABLE: core_vault_records", core["core_vault_records"])
    print_table_summary("PROPOSED TABLE: event_logs", event_logs)

    section("DRY RUN SUMMARY")
    print("This dry run only describes proposed migration mapping.")
    print("No records were written to any DB.")
    print("No local files were modified.")
    print("No local files were deleted.")
    print("No migration was performed.")

    print("\nRecommended next action:")
    print("1. Keep local JSON/JSONL as source of truth for now.")
    print("2. Review KEEP_AS_PROOF vs ARCHIVE_LATER vs DO_NOT_MIGRATE.")
    print("3. Later create a staging DB schema from DATABASE_MIGRATION_PLAN.md.")
    print("4. Only migrate reviewed records into staging first.")


if __name__ == "__main__":
    main()
