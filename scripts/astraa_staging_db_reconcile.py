#!/usr/bin/env python3
"""
Astraa Staging DB Reconciliation

READ-ONLY SCRIPT.

Purpose:
- Compare source-of-truth JSON proof rows against local staging SQLite rows.
- Confirm staging import matches KEEP_AS_PROOF source rows.
- Report missing, extra, and count differences.

Does NOT:
- create a database
- create tables
- create indexes
- insert records
- update records
- delete records
- modify JSON/JSONL source files
"""

from __future__ import annotations

import os
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
USAGE_DB = ROOT / "astraa_data" / "astraa_usage_db.json"
PAYMENT_DB = ROOT / "astraa_data" / "astraa_payment_db.json"
DEFAULT_DB_PATH = ROOT / "astraa_data" / "astraa_staging.db"
SQLITE_PATH = Path(os.getenv("ASTRAA_STAGING_SQLITE_PATH", str(DEFAULT_DB_PATH)))

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


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def is_safe_path(path: Path) -> bool:
    resolved = path.resolve()
    root = ROOT.resolve()

    if not str(resolved).startswith(str(root)):
        return False

    if resolved.suffix != ".db":
        return False

    unsafe = ["prod", "production", "live", "customer", "moneris"]
    return not any(marker in str(resolved).lower() for marker in unsafe)


def load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


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

    if is_test_email(email_l):
        return "ARCHIVE_LATER"

    return "MANUAL_REVIEW"


def classify_payment(record):
    if should_not_migrate_record(record):
        return "DO_NOT_MIGRATE"

    email_l = str(record.get("account_email") or "").lower()

    if (
        email_l in KNOWN_PROOF_EMAILS
        and record.get("verified") is True
        and record.get("receipt_approved") is True
        and record.get("purchase_type") in {
            "subscription_professional",
            "subscription_basic",
            "estimate_pack_10",
        }
    ):
        return "KEEP_AS_PROOF"

    if is_test_email(email_l):
        return "ARCHIVE_LATER"

    return "MANUAL_REVIEW"


def stable_id(prefix, *parts):
    raw = "|".join(str(p or "") for p in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def expected_source_keys():
    usage_db = load_json(USAGE_DB, {})
    payment_db = load_json(PAYMENT_DB, [])

    expected = {
        "accounts": set(),
        "subscriptions": set(),
        "usage_counters": set(),
        "payments": set(),
        "payment_events": set(),
    }

    for email, record in usage_db.items():
        if classify_account(email, record) != "KEEP_AS_PROOF":
            continue

        account_id = record.get("account_id") or email
        selected_tool = record.get("selected_tool") or "Astraa Estimator"
        billing_period_key = record.get("billing_period_key")

        expected["accounts"].add(account_id)
        expected["subscriptions"].add(stable_id("SUB", account_id, selected_tool, billing_period_key))
        expected["usage_counters"].add(stable_id("USAGE", account_id, selected_tool, billing_period_key))

    for record in payment_db:
        if classify_payment(record) != "KEEP_AS_PROOF":
            continue

        payment_id = record.get("payment_id")
        event_id = stable_id(
            "PAYEVT",
            payment_id,
            record.get("verification_source"),
            record.get("created_at")
        )

        expected["payments"].add(payment_id)
        expected["payment_events"].add(event_id)

    return expected


def staging_keys(conn):
    queries = {
        "accounts": "SELECT account_id FROM accounts;",
        "subscriptions": "SELECT subscription_id FROM subscriptions;",
        "usage_counters": "SELECT usage_id FROM usage_counters;",
        "payments": "SELECT payment_id FROM payments;",
        "payment_events": "SELECT event_id FROM payment_events;",
    }

    actual = {}

    for table, sql in queries.items():
        actual[table] = {row[0] for row in conn.execute(sql).fetchall()}

    return actual


def compare_sets(table, expected, actual):
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)

    print(f"\n{table}")
    print("- expected:", len(expected))
    print("- actual:", len(actual))
    print("- missing:", len(missing))
    print("- extra:", len(extra))

    if missing:
        print("  Missing keys:")
        for key in missing:
            print("   -", key)

    if extra:
        print("  Extra keys:")
        for key in extra:
            print("   -", key)

    return not missing and not extra


def main():
    section("ASTRAA STAGING DB RECONCILIATION")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("SQLite path:", SQLITE_PATH)

    if not is_safe_path(SQLITE_PATH):
        section("SAFETY BLOCK")
        print("Refusing to inspect path because it failed local staging safety checks.")
        return

    if not SQLITE_PATH.exists():
        section("STAGING DB STATUS")
        print("Staging DB not created yet.")
        section("READ-ONLY CONFIRMATION")
        print("This script did not create or modify anything.")
        return

    expected = expected_source_keys()

    conn = sqlite3.connect(str(SQLITE_PATH))
    try:
        actual = staging_keys(conn)

        section("RECONCILIATION RESULTS")
        all_ok = True

        for table in ["accounts", "subscriptions", "usage_counters", "payments", "payment_events"]:
            all_ok = compare_sets(table, expected[table], actual[table]) and all_ok

        section("RECONCILIATION SUMMARY")
        if all_ok:
            print("✅ Staging DB matches KEEP_AS_PROOF source keys for imported tables.")
        else:
            print("⚠️ Staging DB differs from KEEP_AS_PROOF source keys. Review missing/extra keys above.")

        section("READ-ONLY CONFIRMATION")
        print("This script inspected source JSON and staging DB keys only.")
        print("This script did not create a database.")
        print("This script did not create tables.")
        print("This script did not create indexes.")
        print("This script did not insert records.")
        print("This script did not update records.")
        print("This script did not delete records.")
        print("This script did not modify JSON/JSONL source files.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
