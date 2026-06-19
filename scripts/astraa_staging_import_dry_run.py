#!/usr/bin/env python3
"""
Astraa Staging Import Dry Run

READ-ONLY SCRIPT.
Builds preview INSERT payloads for future staging DB import.

Does NOT:
- connect to a database
- create a database
- create tables
- insert records
- update records
- delete records
- modify JSON/JSONL files
- write output files

Default behavior:
- Includes KEEP_AS_PROOF records only.
- Skips ARCHIVE_LATER, DO_NOT_MIGRATE, and MANUAL_REVIEW by default.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter


ROOT = Path(".")
USAGE_DB = ROOT / "astraa_data" / "astraa_usage_db.json"
PAYMENT_DB = ROOT / "astraa_data" / "astraa_payment_db.json"
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


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


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
        and record.get("purchase_type") in {"subscription_professional", "subscription_basic", "estimate_pack_10"}
    ):
        return "KEEP_AS_PROOF"

    if is_test_email(email_l):
        return "ARCHIVE_LATER"

    return "MANUAL_REVIEW"


def stable_id(prefix, *parts):
    raw = "|".join(str(p or "") for p in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def account_rows(usage_db):
    rows = []
    for email, record in usage_db.items():
        classification = classify_account(email, record)
        if classification != "KEEP_AS_PROOF":
            continue

        rows.append({
            "table": "accounts",
            "account_id": record.get("account_id") or email,
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

    return rows


def subscription_rows(usage_db):
    rows = []
    for email, record in usage_db.items():
        classification = classify_account(email, record)
        if classification != "KEEP_AS_PROOF":
            continue

        account_id = record.get("account_id") or email
        selected_tool = record.get("selected_tool") or "Astraa Estimator"
        billing_period_key = record.get("billing_period_key")

        rows.append({
            "table": "subscriptions",
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

    return rows


def usage_rows(usage_db):
    rows = []
    for email, record in usage_db.items():
        classification = classify_account(email, record)
        if classification != "KEEP_AS_PROOF":
            continue

        account_id = record.get("account_id") or email
        selected_tool = record.get("selected_tool") or "Astraa Estimator"
        billing_period_key = record.get("billing_period_key")

        rows.append({
            "table": "usage_counters",
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

    return rows


def payment_rows(payment_db):
    rows = []
    for record in payment_db:
        classification = classify_payment(record)
        if classification != "KEEP_AS_PROOF":
            continue

        rows.append({
            "table": "payments",
            "payment_id": record.get("payment_id"),
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
            "verified": record.get("verified"),
            "receipt_request_ok": record.get("receipt_request_ok"),
            "receipt_approved": record.get("receipt_approved"),
            "verification_source": record.get("verification_source"),
            "verification_reason": record.get("verification_reason"),
            "migration_classification": classification,
            "source_system": "astraa_payment_db.json",
            "verified_at": record.get("verified_at"),
            "created_at": record.get("created_at"),
        })

    return rows


def payment_event_rows(payment_db):
    rows = []
    for record in payment_db:
        classification = classify_payment(record)
        if classification != "KEEP_AS_PROOF":
            continue

        payment_id = record.get("payment_id")

        rows.append({
            "table": "payment_events",
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


def classify_core_record(record):
    raw = json.dumps(record, sort_keys=True, default=str).lower()

    if "storage-wrapper-regression-test" in raw or "qa_storage_wrapper_test" in raw:
        return "ARCHIVE_LATER"

    tenant = str(record.get("tenantId") or record.get("tenant_id") or "").lower()
    if "qa" in tenant or "test" in tenant:
        return "ARCHIVE_LATER"

    return "MANUAL_REVIEW"


def core_rows(core_db):
    if not isinstance(core_db, dict):
        core_db = {}

    output = {
        "core_entities": [],
        "core_activity": [],
        "core_events": [],
        "core_vault_records": [],
    }

    for record in core_db.get("entities", []):
        classification = classify_core_record(record)
        if classification != "KEEP_AS_PROOF":
            continue

        output["core_entities"].append({
            "table": "core_entities",
            "entity_id": record.get("entityId"),
            "tenant_id": record.get("tenantId"),
            "entity_type": record.get("entityType"),
            "name": record.get("name"),
            "project_id": record.get("projectId"),
            "location": record.get("location"),
            "sector": record.get("sector"),
            "data_json": json.dumps(record.get("data") or {}, sort_keys=True),
            "source_system": "astraa_core_os_store.json",
            "migration_classification": classification,
            "created_at": record.get("createdAt"),
            "updated_at": record.get("updatedAt"),
        })

    for record in core_db.get("activity", []):
        classification = classify_core_record(record)
        if classification != "KEEP_AS_PROOF":
            continue

        output["core_activity"].append({
            "table": "core_activity",
            "activity_id": record.get("activityId"),
            "tenant_id": record.get("tenantId"),
            "project_id": record.get("projectId"),
            "event_type": record.get("eventType"),
            "tool": record.get("tool"),
            "summary": record.get("summary"),
            "related_json": json.dumps(record.get("related") or {}, sort_keys=True),
            "source_system": "astraa_core_os_store.json",
            "migration_classification": classification,
            "created_at": record.get("timestamp"),
        })

    for record in core_db.get("events", []):
        classification = classify_core_record(record)
        if classification != "KEEP_AS_PROOF":
            continue

        output["core_events"].append({
            "table": "core_events",
            "event_id": record.get("eventId"),
            "tenant_id": record.get("tenantId"),
            "project_id": record.get("projectId"),
            "event_type": record.get("eventType"),
            "tool": record.get("tool"),
            "payload_json": json.dumps(record.get("payload") or {}, sort_keys=True),
            "source_system": "astraa_core_os_store.json",
            "migration_classification": classification,
            "created_at": record.get("timestamp"),
        })

    for record in core_db.get("vaultRecords", []):
        classification = classify_core_record(record)
        if classification != "KEEP_AS_PROOF":
            continue

        output["core_vault_records"].append({
            "table": "core_vault_records",
            "vault_record_id": record.get("vaultRecordId"),
            "tenant_id": record.get("tenantId"),
            "project_id": record.get("projectId"),
            "estimate_id": record.get("estimateId"),
            "record_type": record.get("recordType"),
            "source_tool": record.get("sourceTool"),
            "source_gateway": record.get("sourceGateway"),
            "visibility": record.get("visibility"),
            "zero_knowledge_ready": record.get("zeroKnowledgeReady"),
            "linked_payloads_json": json.dumps(record.get("linkedPayloads") or {}, sort_keys=True),
            "stored_objects_json": json.dumps(record.get("storedObjects") or [], sort_keys=True),
            "data_json": json.dumps(record.get("data") or {}, sort_keys=True),
            "audit_json": json.dumps(record.get("audit") or {}, sort_keys=True),
            "source_system": "astraa_core_os_store.json",
            "migration_classification": classification,
            "created_at": (record.get("audit") or {}).get("createdAt"),
            "updated_at": (record.get("audit") or {}).get("updatedAt"),
        })

    return output


def print_rows(title, rows, sample_limit=5):
    section(title)
    print("Preview row count:", len(rows))

    if not rows:
        print("No rows selected for import preview.")
        return

    classifications = Counter(row.get("migration_classification") for row in rows)
    print("Classification counts:")
    for key, value in classifications.most_common():
        print(f"  {key}: {value}")

    print("\nSample preview rows:")
    for row in rows[:sample_limit]:
        print(json.dumps(row, indent=2, sort_keys=True))


def main():
    section("ASTRAA STAGING IMPORT DRY RUN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    usage_db = load_json(USAGE_DB, {})
    payment_db = load_json(PAYMENT_DB, [])
    core_db = load_json(CORE_OS_DB, {})

    rows = {
        "accounts": account_rows(usage_db),
        "subscriptions": subscription_rows(usage_db),
        "usage_counters": usage_rows(usage_db),
        "payments": payment_rows(payment_db),
        "payment_events": payment_event_rows(payment_db),
    }

    rows.update(core_rows(core_db))

    total = 0
    for table_name, table_rows in rows.items():
        total += len(table_rows)
        print_rows(f"IMPORT PREVIEW: {table_name}", table_rows)

    section("IMPORT DRY RUN SUMMARY")
    print("Total preview rows selected:", total)
    print("Default selection policy: KEEP_AS_PROOF only.")
    print("")
    print("No DB connection was opened.")
    print("No records were inserted.")
    print("No local files were modified.")
    print("No migration was performed.")

    print("\nRecommended next action:")
    print("1. Review preview rows.")
    print("2. Keep ARCHIVE_LATER and DO_NOT_MIGRATE excluded.")
    print("3. Create staging DB only when ready using guarded template.")
    print("4. Add a guarded staging import script only after reviewing this preview.")


if __name__ == "__main__":
    main()
