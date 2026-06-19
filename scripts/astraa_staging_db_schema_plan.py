#!/usr/bin/env python3
"""
Astraa Staging DB Schema Plan

READ-ONLY SCRIPT.
Prints proposed SQL DDL for future staging database tables.

Does NOT:
- connect to a database
- create tables
- modify files
- migrate data
- delete data

Purpose:
- Translate DATABASE_MIGRATION_PLAN.md and dry-run table names into a concrete staging schema draft.
"""

from __future__ import annotations

from datetime import datetime, timezone


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


SCHEMA = {
    "accounts": """
CREATE TABLE accounts (
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
    "subscriptions": """
CREATE TABLE subscriptions (
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
    "usage_counters": """
CREATE TABLE usage_counters (
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
    "payments": """
CREATE TABLE payments (
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
    verified BOOLEAN,
    receipt_request_ok BOOLEAN,
    receipt_approved BOOLEAN,
    verification_source TEXT,
    verification_reason TEXT,
    migration_classification TEXT,
    source_system TEXT,
    verified_at TIMESTAMP,
    created_at TIMESTAMP
);
""",
    "payment_events": """
CREATE TABLE payment_events (
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
    "core_entities": """
CREATE TABLE core_entities (
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
    "core_activity": """
CREATE TABLE core_activity (
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
    "core_events": """
CREATE TABLE core_events (
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
    "core_vault_records": """
CREATE TABLE core_vault_records (
    vault_record_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    project_id TEXT,
    estimate_id TEXT,
    record_type TEXT,
    source_tool TEXT,
    source_gateway TEXT,
    visibility TEXT,
    zero_knowledge_ready BOOLEAN,
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
    "event_logs": """
CREATE TABLE event_logs (
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
"""
}


def main():
    section("ASTRAA STAGING DB SCHEMA PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("PROPOSED TABLE ORDER")
    for idx, table_name in enumerate(SCHEMA.keys(), 1):
        print(f"{idx}. {table_name}")

    section("PROPOSED SQL DDL")
    for table_name, ddl in SCHEMA.items():
        print(f"\n-- TABLE: {table_name}")
        print(ddl.strip())

    section("READ-ONLY CONFIRMATION")
    print("This script did not connect to a database.")
    print("This script did not create tables.")
    print("This script did not migrate data.")
    print("This script did not modify local files.")

    print("\nRecommended next action:")
    print("1. Review this schema against DATABASE_MIGRATION_PLAN.md.")
    print("2. Add indexes/constraints after review.")
    print("3. Create staging DB only after schema is approved.")
    print("4. Run migration dry-run again before any staging import.")


if __name__ == "__main__":
    main()
