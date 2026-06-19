#!/usr/bin/env python3
"""
Astraa Staging DB Creation Template

SAFE BY DEFAULT.

Default behavior:
- Does NOT create a database.
- Prints refusal and instructions.

Optional guarded behavior:
- Creates a local SQLite staging database ONLY when:
  ASTRAA_ALLOW_STAGING_DB_CREATE=true
  ASTRAA_STAGING_DB_ENGINE=sqlite
  ASTRAA_STAGING_SQLITE_PATH is set to a safe local staging path

Does NOT:
- migrate data
- read/write production DB
- delete files
- modify JSON/JSONL source data
- connect to external services
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

ALLOW_CREATE = os.getenv("ASTRAA_ALLOW_STAGING_DB_CREATE", "false").strip().lower() == "true"
ENGINE = os.getenv("ASTRAA_STAGING_DB_ENGINE", "sqlite").strip().lower()
SQLITE_PATH = os.getenv(
    "ASTRAA_STAGING_SQLITE_PATH",
    str(ROOT / "astraa_data" / "astraa_staging.db")
)


SCHEMA_SQL = [
    """
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    primary_email TEXT NOT NULL UNIQUE,
    display_name TEXT,
    business_name TEXT,
    account_type TEXT,
    status TEXT,
    migration_classification TEXT,
    source_system TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
""",
    """
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    tenant_id TEXT,
    selected_tool TEXT NOT NULL,
    selected_plan TEXT,
    payment_status TEXT,
    subscription_status TEXT,
    billing_period_key TEXT,
    billing_period_start DATE,
    billing_period_end DATE,
    estimate_limit INTEGER,
    migration_classification TEXT,
    source_system TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
""",
    """
CREATE TABLE IF NOT EXISTS usage_counters (
    usage_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    tenant_id TEXT,
    selected_tool TEXT NOT NULL,
    billing_period_key TEXT,
    estimate_limit INTEGER,
    estimate_used INTEGER,
    extra_estimate_credits_total INTEGER,
    extra_estimate_credits_used INTEGER,
    last_trial_estimate_date DATE,
    migration_classification TEXT,
    source_system TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    UNIQUE (account_id, selected_tool, billing_period_key)
);
""",
    """
CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    account_id TEXT,
    account_email TEXT,
    tenant_id TEXT,
    selected_tool TEXT,
    selected_plan TEXT,
    purchase_type TEXT,
    payment_gateway TEXT,
    environment TEXT,
    idempotency_key TEXT,
    ticket_reference TEXT,
    verified INTEGER,
    receipt_request_ok INTEGER,
    receipt_approved INTEGER,
    verification_source TEXT,
    verification_reason TEXT,
    migration_classification TEXT,
    source_system TEXT,
    verified_at TIMESTAMP,
    created_at TIMESTAMP
);
""",
    """
CREATE TABLE IF NOT EXISTS payment_events (
    event_id TEXT PRIMARY KEY,
    payment_id TEXT,
    account_id TEXT,
    account_email TEXT,
    tenant_id TEXT,
    event_type TEXT,
    event_status TEXT,
    event_reason TEXT,
    safe_gateway_reference TEXT,
    migration_classification TEXT,
    source_system TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
);
""",
    """
CREATE TABLE IF NOT EXISTS core_entities (
    entity_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    entity_type TEXT,
    name TEXT,
    project_id TEXT,
    location TEXT,
    sector TEXT,
    data_json TEXT,
    source_system TEXT,
    migration_classification TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
""",
    """
CREATE TABLE IF NOT EXISTS core_activity (
    activity_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    project_id TEXT,
    event_type TEXT,
    tool TEXT,
    summary TEXT,
    related_json TEXT,
    source_system TEXT,
    migration_classification TEXT,
    created_at TIMESTAMP
);
""",
    """
CREATE TABLE IF NOT EXISTS core_events (
    event_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    project_id TEXT,
    event_type TEXT,
    tool TEXT,
    payload_json TEXT,
    source_system TEXT,
    migration_classification TEXT,
    created_at TIMESTAMP
);
""",
    """
CREATE TABLE IF NOT EXISTS core_vault_records (
    vault_record_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    project_id TEXT,
    estimate_id TEXT,
    record_type TEXT,
    source_tool TEXT,
    source_gateway TEXT,
    visibility TEXT,
    zero_knowledge_ready INTEGER,
    linked_payloads_json TEXT,
    stored_objects_json TEXT,
    data_json TEXT,
    audit_json TEXT,
    source_system TEXT,
    migration_classification TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
""",
    """
CREATE TABLE IF NOT EXISTS event_logs (
    event_log_id TEXT PRIMARY KEY,
    log_name TEXT,
    source_file TEXT,
    source_line INTEGER,
    status TEXT,
    email TEXT,
    timestamp TIMESTAMP,
    payload_json TEXT,
    migration_classification TEXT,
    source_system TEXT,
    created_at TIMESTAMP
);
""",
]


INDEX_SQL = [
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_primary_email_unique ON accounts (primary_email);",
    "CREATE INDEX IF NOT EXISTS idx_accounts_migration_classification ON accounts (migration_classification);",
    "CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts (status);",

    "CREATE INDEX IF NOT EXISTS idx_subscriptions_account_id ON subscriptions (account_id);",
    "CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant_id ON subscriptions (tenant_id);",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_subscriptions_account_tool_period_unique ON subscriptions (account_id, selected_tool, billing_period_key);",
    "CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_status ON subscriptions (selected_plan, payment_status, subscription_status);",

    "CREATE UNIQUE INDEX IF NOT EXISTS idx_usage_account_tool_period_unique ON usage_counters (account_id, selected_tool, billing_period_key);",
    "CREATE INDEX IF NOT EXISTS idx_usage_account_id ON usage_counters (account_id);",
    "CREATE INDEX IF NOT EXISTS idx_usage_billing_period ON usage_counters (billing_period_key);",

    "CREATE UNIQUE INDEX IF NOT EXISTS idx_payments_idempotency_key_unique ON payments (idempotency_key);",
    "CREATE INDEX IF NOT EXISTS idx_payments_account_purchase_ticket ON payments (account_email, purchase_type, ticket_reference);",
    "CREATE INDEX IF NOT EXISTS idx_payments_verified_receipt ON payments (verified, receipt_approved);",
    "CREATE INDEX IF NOT EXISTS idx_payments_account_email ON payments (account_email);",
    "CREATE INDEX IF NOT EXISTS idx_payments_migration_classification ON payments (migration_classification);",

    "CREATE INDEX IF NOT EXISTS idx_payment_events_payment_id ON payment_events (payment_id);",
    "CREATE INDEX IF NOT EXISTS idx_payment_events_type_status ON payment_events (event_type, event_status);",
    "CREATE INDEX IF NOT EXISTS idx_payment_events_safe_gateway_reference ON payment_events (safe_gateway_reference);",

    "CREATE INDEX IF NOT EXISTS idx_core_entities_tenant_entity_type ON core_entities (tenant_id, entity_type);",
    "CREATE INDEX IF NOT EXISTS idx_core_entities_project_id ON core_entities (project_id);",
    "CREATE INDEX IF NOT EXISTS idx_core_entities_name ON core_entities (name);",

    "CREATE INDEX IF NOT EXISTS idx_core_activity_tenant_created ON core_activity (tenant_id, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_core_activity_project_id ON core_activity (project_id);",
    "CREATE INDEX IF NOT EXISTS idx_core_activity_event_type ON core_activity (event_type);",

    "CREATE INDEX IF NOT EXISTS idx_core_events_tenant_created ON core_events (tenant_id, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_core_events_project_id ON core_events (project_id);",
    "CREATE INDEX IF NOT EXISTS idx_core_events_event_type ON core_events (event_type);",

    "CREATE INDEX IF NOT EXISTS idx_core_vault_tenant_project ON core_vault_records (tenant_id, project_id);",
    "CREATE INDEX IF NOT EXISTS idx_core_vault_estimate_id ON core_vault_records (estimate_id);",
    "CREATE INDEX IF NOT EXISTS idx_core_vault_record_type ON core_vault_records (record_type);",

    "CREATE INDEX IF NOT EXISTS idx_event_logs_log_name_timestamp ON event_logs (log_name, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_event_logs_email ON event_logs (email);",
    "CREATE INDEX IF NOT EXISTS idx_event_logs_source_file_line ON event_logs (source_file, source_line);",
    "CREATE INDEX IF NOT EXISTS idx_event_logs_migration_classification ON event_logs (migration_classification);",
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

    path_l = str(resolved).lower()

    unsafe_markers = [
        "prod",
        "production",
        "live",
        "customer",
        "moneris",
    ]

    if any(marker in path_l for marker in unsafe_markers):
        return False

    if resolved.suffix != ".db":
        return False

    return True


def print_plan():
    section("ASTRAA STAGING DB CREATION TEMPLATE")
    print("Mode:", "CREATE ENABLED" if ALLOW_CREATE else "DRY RUN / REFUSAL BY DEFAULT")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Engine:", ENGINE)
    print("SQLite path:", SQLITE_PATH)

    section("SAFETY STATUS")
    if not ALLOW_CREATE:
        print("Refusing to create staging DB because ASTRAA_ALLOW_STAGING_DB_CREATE is not true.")
        print("")
        print("To intentionally create a LOCAL staging SQLite DB only, run:")
        print("export ASTRAA_ALLOW_STAGING_DB_CREATE=true")
        print("export ASTRAA_STAGING_DB_ENGINE=sqlite")
        print("export ASTRAA_STAGING_SQLITE_PATH=astraa_data/astraa_staging.db")
        print("python3 scripts/astraa_staging_db_create_template.py")
        return False

    if ENGINE != "sqlite":
        print("Refusing to create staging DB because only sqlite is supported by this local template.")
        return False

    db_path = Path(SQLITE_PATH)

    if not is_safe_sqlite_path(db_path):
        print("Refusing to create staging DB because ASTRAA_STAGING_SQLITE_PATH failed safety checks.")
        print("Use a local non-production path like astraa_data/astraa_staging.db")
        return False

    return True


def create_sqlite_db():
    db_path = Path(SQLITE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys = ON;")

        for statement in SCHEMA_SQL:
            conn.executescript(statement)

        for statement in INDEX_SQL:
            conn.execute(statement)

        conn.commit()

        section("STAGING SQLITE DB CREATED")
        print("Created/verified local staging DB:", db_path)
        print("Tables/indexes were created if missing.")
        print("No data was migrated.")
        print("JSON/JSONL source files were not modified.")
    finally:
        conn.close()


def main():
    allowed = print_plan()

    if not allowed:
        section("READ-ONLY CONFIRMATION")
        print("This script did not create a database.")
        print("This script did not create tables.")
        print("This script did not create indexes.")
        print("This script did not migrate data.")
        print("This script did not modify JSON/JSONL source files.")
        return

    create_sqlite_db()


if __name__ == "__main__":
    main()
