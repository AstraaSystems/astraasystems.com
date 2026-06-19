#!/usr/bin/env python3
"""
Astraa Staging DB Index and Constraint Plan

READ-ONLY SCRIPT.
Prints proposed indexes and constraints for the future staging database.

Does NOT:
- connect to a database
- create indexes
- create constraints
- modify files
- migrate data

Purpose:
- Strengthen the staging schema plan before any DB creation.
- Protect payment idempotency, usage uniqueness, tenant isolation, and Core OS lookup paths.
"""

from __future__ import annotations

from datetime import datetime, timezone


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


INDEXES_AND_CONSTRAINTS = {
    "accounts": [
        """
-- Ensure email lookup is fast and unique.
CREATE UNIQUE INDEX idx_accounts_primary_email_unique
ON accounts (primary_email);
""",
        """
-- Help filter migrated/proof/archive records.
CREATE INDEX idx_accounts_migration_classification
ON accounts (migration_classification);
""",
        """
-- Help account status dashboards.
CREATE INDEX idx_accounts_status
ON accounts (status);
""",
    ],
    "subscriptions": [
        """
-- Fast lookup by account.
CREATE INDEX idx_subscriptions_account_id
ON subscriptions (account_id);
""",
        """
-- Fast lookup by tenant.
CREATE INDEX idx_subscriptions_tenant_id
ON subscriptions (tenant_id);
""",
        """
-- Prevent duplicate active tool/period subscription rows during migration.
CREATE UNIQUE INDEX idx_subscriptions_account_tool_period_unique
ON subscriptions (account_id, selected_tool, billing_period_key);
""",
        """
-- Plan/status reporting.
CREATE INDEX idx_subscriptions_plan_status
ON subscriptions (selected_plan, payment_status, subscription_status);
""",
    ],
    "usage_counters": [
        """
-- Enforce one usage counter per account/tool/billing period.
CREATE UNIQUE INDEX idx_usage_account_tool_period_unique
ON usage_counters (account_id, selected_tool, billing_period_key);
""",
        """
-- Fast account usage lookup.
CREATE INDEX idx_usage_account_id
ON usage_counters (account_id);
""",
        """
-- Usage period reporting.
CREATE INDEX idx_usage_billing_period
ON usage_counters (billing_period_key);
""",
    ],
    "payments": [
        """
-- Payment idempotency protection.
-- Should be unique when idempotency_key is present.
CREATE UNIQUE INDEX idx_payments_idempotency_key_unique
ON payments (idempotency_key);
""",
        """
-- Prevent duplicate application of the same ticket/account/purchase type.
CREATE INDEX idx_payments_account_purchase_ticket
ON payments (account_email, purchase_type, ticket_reference);
""",
        """
-- Payment proof lookup.
CREATE INDEX idx_payments_verified_receipt
ON payments (verified, receipt_approved);
""",
        """
-- Payment account lookup.
CREATE INDEX idx_payments_account_email
ON payments (account_email);
""",
        """
-- Migration filtering.
CREATE INDEX idx_payments_migration_classification
ON payments (migration_classification);
""",
    ],
    "payment_events": [
        """
-- Payment event lookup.
CREATE INDEX idx_payment_events_payment_id
ON payment_events (payment_id);
""",
        """
-- Payment event timeline/reporting.
CREATE INDEX idx_payment_events_type_status
ON payment_events (event_type, event_status);
""",
        """
-- Safe gateway reference lookup for audit.
CREATE INDEX idx_payment_events_safe_gateway_reference
ON payment_events (safe_gateway_reference);
""",
    ],
    "core_entities": [
        """
-- Tenant-scoped entity lookup.
CREATE INDEX idx_core_entities_tenant_entity_type
ON core_entities (tenant_id, entity_type);
""",
        """
-- Project lookup.
CREATE INDEX idx_core_entities_project_id
ON core_entities (project_id);
""",
        """
-- Core search support.
CREATE INDEX idx_core_entities_name
ON core_entities (name);
""",
    ],
    "core_activity": [
        """
-- Tenant activity stream lookup.
CREATE INDEX idx_core_activity_tenant_created
ON core_activity (tenant_id, created_at);
""",
        """
-- Project activity lookup.
CREATE INDEX idx_core_activity_project_id
ON core_activity (project_id);
""",
        """
-- Event type filtering.
CREATE INDEX idx_core_activity_event_type
ON core_activity (event_type);
""",
    ],
    "core_events": [
        """
-- Tenant event timeline lookup.
CREATE INDEX idx_core_events_tenant_created
ON core_events (tenant_id, created_at);
""",
        """
-- Project event lookup.
CREATE INDEX idx_core_events_project_id
ON core_events (project_id);
""",
        """
-- Automation/event routing lookup.
CREATE INDEX idx_core_events_event_type
ON core_events (event_type);
""",
    ],
    "core_vault_records": [
        """
-- Tenant Vault lookup.
CREATE INDEX idx_core_vault_tenant_project
ON core_vault_records (tenant_id, project_id);
""",
        """
-- Estimate/Vault lookup.
CREATE INDEX idx_core_vault_estimate_id
ON core_vault_records (estimate_id);
""",
        """
-- Record type filtering.
CREATE INDEX idx_core_vault_record_type
ON core_vault_records (record_type);
""",
    ],
    "event_logs": [
        """
-- Event log timeline lookup.
CREATE INDEX idx_event_logs_log_name_timestamp
ON event_logs (log_name, timestamp);
""",
        """
-- Event log email lookup.
CREATE INDEX idx_event_logs_email
ON event_logs (email);
""",
        """
-- Event log source traceability.
CREATE INDEX idx_event_logs_source_file_line
ON event_logs (source_file, source_line);
""",
        """
-- Migration filtering.
CREATE INDEX idx_event_logs_migration_classification
ON event_logs (migration_classification);
""",
    ],
}


def main():
    section("ASTRAA STAGING DB INDEX AND CONSTRAINT PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    section("PROPOSED INDEX / CONSTRAINT ORDER")
    count = 0
    for table_name, statements in INDEXES_AND_CONSTRAINTS.items():
        for _ in statements:
            count += 1
            print(f"{count}. {table_name}")

    section("PROPOSED SQL")
    for table_name, statements in INDEXES_AND_CONSTRAINTS.items():
        print(f"\n-- TABLE: {table_name}")
        for statement in statements:
            print(statement.strip())
            print()

    section("READ-ONLY CONFIRMATION")
    print("This script did not connect to a database.")
    print("This script did not create indexes.")
    print("This script did not create constraints.")
    print("This script did not modify local files.")
    print("This script did not migrate data.")

    print("\nRecommended next action:")
    print("1. Review these indexes with scripts/astraa_staging_db_schema_plan.py.")
    print("2. Confirm DB engine choice before using syntax directly.")
    print("3. Keep JSON/JSONL as source of truth until staging DB is created and validated.")
    print("4. Do not run real DB creation until schema/index plan is reviewed.")


if __name__ == "__main__":
    main()
