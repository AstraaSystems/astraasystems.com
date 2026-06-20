#!/usr/bin/env python3
"""
Astraa Guarded Staging Import

SAFE BY DEFAULT.

Default behavior:
- Refuses to import unless ASTRAA_ALLOW_STAGING_IMPORT=true.
- Refuses if staging DB does not exist.
- Refuses if required tables are missing.
- Imports KEEP_AS_PROOF records only.
- Never imports ARCHIVE_LATER, DO_NOT_MIGRATE, or MANUAL_REVIEW.

This script is intended for local staging SQLite only.
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

ALLOW_IMPORT = os.getenv("ASTRAA_ALLOW_STAGING_IMPORT", "false").strip().lower() == "true"
ENGINE = os.getenv("ASTRAA_STAGING_DB_ENGINE", "sqlite").strip().lower()
SQLITE_PATH = Path(
    os.getenv(
        "ASTRAA_STAGING_SQLITE_PATH",
        str(ROOT / "astraa_data" / "astraa_staging.db")
    )
)

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

REQUIRED_TABLES = [
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
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def is_safe_sqlite_path(path: Path) -> bool:
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
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        raise RuntimeError(f"Could not parse {path}: {exc}")


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
            "estimate_pack_10"
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


def build_import_rows():
    usage_db = load_json(USAGE_DB, {})
    payment_db = load_json(PAYMENT_DB, [])

    rows = {
        "accounts": [],
        "subscriptions": [],
        "usage_counters": [],
        "payments": [],
        "payment_events": [],
    }

    for email, record in usage_db.items():
        classification = classify_account(email, record)
        if classification != "KEEP_AS_PROOF":
            continue

        account_id = record.get("account_id") or email
        selected_tool = record.get("selected_tool") or "Astraa Estimator"
        billing_period_key = record.get("billing_period_key")

        rows["accounts"].append({
            "account_id": account_id,
            "primary_email": email,
            "display_name": None,
            "business_name": None,
            "account_type": "internal_proof",
            "status": record.get("payment_status"),
            "migration_classification": classification,
            "source_system": "astraa_usage_db.json",
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        })

        rows["subscriptions"].append({
            "subscription_id": stable_id("SUB", account_id, selected_tool, billing_period_key),
            "account_id": account_id,
            "tenant_id": record.get("tenant_id"),
            "selected_tool": selected_tool,
            "selected_plan": record.get("selected_plan") or record.get("plan"),
            "payment_status": record.get("payment_status"),
            "subscription_status": record.get("subscription_status"),
            "billing_period_key": billing_period_key,
            "billing_period_start": record.get("billing_period_start"),
            "billing_period_end": record.get("billing_period_end"),
            "estimate_limit": record.get("estimate_limit"),
            "migration_classification": classification,
            "source_system": "astraa_usage_db.json",
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        })

        rows["usage_counters"].append({
            "usage_id": stable_id("USAGE", account_id, selected_tool, billing_period_key),
            "account_id": account_id,
            "tenant_id": record.get("tenant_id"),
            "selected_tool": selected_tool,
            "billing_period_key": billing_period_key,
            "estimate_limit": record.get("estimate_limit"),
            "estimate_used": record.get("estimate_used"),
            "extra_estimate_credits_total": record.get("extra_estimate_credits_total"),
            "extra_estimate_credits_used": record.get("extra_estimate_credits_used"),
            "last_trial_estimate_date": record.get("last_trial_estimate_date"),
            "migration_classification": classification,
            "source_system": "astraa_usage_db.json",
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        })

    for record in payment_db:
        classification = classify_payment(record)
        if classification != "KEEP_AS_PROOF":
            continue

        payment_id = record.get("payment_id")

        rows["payments"].append({
            "payment_id": payment_id,
            "account_id": record.get("account_email"),
            "account_email": record.get("account_email"),
            "tenant_id": record.get("tenant_id"),
            "selected_tool": record.get("selected_tool"),
            "selected_plan": record.get("selected_plan"),
            "purchase_type": record.get("purchase_type"),
            "payment_gateway": record.get("gateway") or "Moneris",
            "environment": record.get("environment"),
            "idempotency_key": record.get("idempotency_key"),
            "ticket_reference": record.get("ticket_reference"),
            "verified": 1 if record.get("verified") else 0,
            "receipt_request_ok": 1 if record.get("receipt_request_ok") else 0,
            "receipt_approved": 1 if record.get("receipt_approved") else 0,
            "verification_source": record.get("verification_source"),
            "verification_reason": record.get("verification_reason"),
            "migration_classification": classification,
            "source_system": "astraa_payment_db.json",
            "verified_at": record.get("verified_at"),
            "created_at": record.get("created_at"),
        })

        rows["payment_events"].append({
            "event_id": stable_id("PAYEVT", payment_id, record.get("verification_source"), record.get("created_at")),
            "payment_id": payment_id,
            "account_id": record.get("account_email"),
            "account_email": record.get("account_email"),
            "tenant_id": record.get("tenant_id"),
            "event_type": "payment_verification_record",
            "event_status": "verified" if record.get("verified") else "not_verified",
            "event_reason": record.get("verification_reason"),
            "safe_gateway_reference": record.get("ticket_reference"),
            "migration_classification": classification,
            "source_system": "astraa_payment_db.json",
            "created_at": record.get("created_at"),
        })

    return rows


def ensure_required_tables(conn):
    existing = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
    }

    missing = [table for table in REQUIRED_TABLES if table not in existing]

    if missing:
        raise RuntimeError("Missing required staging tables: " + ", ".join(missing))


def insert_rows(conn, table, rows):
    if not rows:
        return 0

    inserted = 0

    for row in rows:
        columns = list(row.keys())
        placeholders = ", ".join(["?"] * len(columns))
        col_sql = ", ".join(columns)
        sql = f"INSERT OR IGNORE INTO {table} ({col_sql}) VALUES ({placeholders});"
        values = [row[col] for col in columns]
        cursor = conn.execute(sql, values)
        inserted += cursor.rowcount if cursor.rowcount is not None else 0

    return inserted


def safety_gate():
    section("ASTRAA GUARDED STAGING IMPORT")
    print("Mode:", "IMPORT ENABLED" if ALLOW_IMPORT else "DRY RUN / REFUSAL BY DEFAULT")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Engine:", ENGINE)
    print("SQLite path:", SQLITE_PATH)

    if not ALLOW_IMPORT:
        section("SAFETY STATUS")
        print("Refusing to import because ASTRAA_ALLOW_STAGING_IMPORT is not true.")
        print("")
        print("To intentionally import KEEP_AS_PROOF rows into LOCAL staging SQLite only:")
        print("export ASTRAA_ALLOW_STAGING_IMPORT=true")
        print("export ASTRAA_STAGING_DB_ENGINE=sqlite")
        print("export ASTRAA_STAGING_SQLITE_PATH=astraa_data/astraa_staging.db")
        print("python3 scripts/astraa_staging_import_guarded.py")
        return False

    if ENGINE != "sqlite":
        print("Refusing to import because only sqlite is supported by this local guarded importer.")
        return False

    if not is_safe_sqlite_path(SQLITE_PATH):
        print("Refusing to import because ASTRAA_STAGING_SQLITE_PATH failed safety checks.")
        return False

    if not SQLITE_PATH.exists():
        print("Refusing to import because staging DB does not exist.")
        print("Create it intentionally first with scripts/astraa_staging_db_create_template.py")
        return False

    return True


def main():
    allowed = safety_gate()
    rows = build_import_rows()
    total_preview = sum(len(v) for v in rows.values())

    section("IMPORT SELECTION SUMMARY")
    print("Selection policy: KEEP_AS_PROOF only")
    print("Preview rows selected:", total_preview)

    for table, table_rows in rows.items():
        print(f"{table}: {len(table_rows)}")

    if not allowed:
        section("READ-ONLY CONFIRMATION")
        print("This script did not connect to a database.")
        print("This script did not insert records.")
        print("This script did not modify JSON/JSONL source files.")
        print("This script did not perform migration.")
        return

    conn = sqlite3.connect(str(SQLITE_PATH))
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        ensure_required_tables(conn)

        inserted_counts = {}

        for table in ["accounts", "subscriptions", "usage_counters", "payments", "payment_events"]:
            inserted_counts[table] = insert_rows(conn, table, rows[table])

        conn.commit()

        section("IMPORT COMPLETED INTO LOCAL STAGING SQLITE")
        print("Only KEEP_AS_PROOF rows were eligible.")
        print("Inserted row counts:")

        for table, count in inserted_counts.items():
            print(f"{table}: {count}")

        print("")
        print("JSON/JSONL source files were not modified.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
