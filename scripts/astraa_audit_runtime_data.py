#!/usr/bin/env python3
"""
Astraa Runtime Data Audit

READ-ONLY SCRIPT.
This script does not delete, modify, write, archive, migrate, or repair data.

Purpose:
- Audit local runtime JSON/JSONL files before public launch hardening.
- Identify test/internal accounts.
- Identify suspicious or unsupported payment records.
- Summarize active/inactive usage records.
- Help prepare cleanup planning safely.

Files inspected:
- astraa_data/astraa_usage_db.json
- astraa_data/astraa_payment_db.json
- preloads.jsonl
- payments.jsonl
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime


ROOT = Path(".")
USAGE_DB = ROOT / "astraa_data" / "astraa_usage_db.json"
PAYMENT_DB = ROOT / "astraa_data" / "astraa_payment_db.json"
PRELOADS_JSONL = ROOT / "preloads.jsonl"
PAYMENTS_JSONL = ROOT / "payments.jsonl"


ALLOWED_PURCHASE_TYPES = {
    "subscription_trial",
    "subscription_basic",
    "subscription_professional",
    "subscription_custom",
    "estimate_pack",
    "estimate_pack_10",
    "extra_estimate_pack",
    "extra_estimate_pack_10",
}


TEST_EMAIL_MARKERS = [
    "test",
    "approved",
    "live.test",
    "astraa.live.test",
    "approved.live.test",
    "approved.card.live.test",
    "malicious-change",
    "keshanth.sivayo@gmail.com",
]


def load_json(path: Path, fallback):
    if not path.exists():
        return fallback

    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        print(f"⚠️ Could not parse JSON file: {path} :: {exc}")
        return fallback


def load_jsonl(path: Path):
    rows = []

    if not path.exists():
        return rows

    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        line = line.strip()
        if not line:
            continue

        try:
            rows.append(json.loads(line))
        except Exception as exc:
            rows.append({
                "_parse_error": str(exc),
                "_line_number": idx,
                "_raw": line[:500],
            })

    return rows


def ticket_suffix(value):
    value = str(value or "")
    if not value:
        return ""
    return value[-12:]


def is_test_email(email):
    email_l = str(email or "").lower()
    return any(marker in email_l for marker in TEST_EMAIL_MARKERS)


def print_section(title):
    print("\n" + "=" * 96)
    print(title)
    print("=" * 96)


def summarize_usage_db(usage_db):
    print_section("USAGE DB SUMMARY")

    if not isinstance(usage_db, dict) or not usage_db:
        print("No usage records found.")
        return

    print("Total usage accounts:", len(usage_db))

    payment_status_counts = Counter()
    subscription_status_counts = Counter()
    plan_counts = Counter()

    test_accounts = []
    active_accounts = []
    inactive_accounts = []

    for email, record in usage_db.items():
        if not isinstance(record, dict):
            continue

        payment_status = record.get("payment_status")
        subscription_status = record.get("subscription_status")
        selected_plan = record.get("selected_plan") or record.get("plan")

        payment_status_counts[str(payment_status)] += 1
        subscription_status_counts[str(subscription_status)] += 1
        plan_counts[str(selected_plan)] += 1

        item = {
            "email": email,
            "account_id": record.get("account_id"),
            "selected_plan": selected_plan,
            "payment_status": payment_status,
            "subscription_status": subscription_status,
            "estimate_limit": record.get("estimate_limit"),
            "estimate_used": record.get("estimate_used"),
            "extra_estimate_credits_total": record.get("extra_estimate_credits_total"),
            "extra_estimate_credits_used": record.get("extra_estimate_credits_used"),
            "local_test_note": record.get("local_test_note"),
        }

        if is_test_email(email):
            test_accounts.append(item)

        if payment_status == "active" or subscription_status == "active":
            active_accounts.append(item)
        else:
            inactive_accounts.append(item)

    print("\nPayment status counts:")
    for key, value in payment_status_counts.most_common():
        print(f"  {key}: {value}")

    print("\nSubscription status counts:")
    for key, value in subscription_status_counts.most_common():
        print(f"  {key}: {value}")

    print("\nPlan counts:")
    for key, value in plan_counts.most_common():
        print(f"  {key}: {value}")

    print("\nActive accounts:")
    if not active_accounts:
        print("  None")
    for account in active_accounts:
        print(json.dumps(account, indent=2, sort_keys=True))

    print("\nInactive accounts:")
    if not inactive_accounts:
        print("  None")
    for account in inactive_accounts:
        print(json.dumps(account, indent=2, sort_keys=True))

    print("\nLikely internal/test accounts:")
    if not test_accounts:
        print("  None")
    for account in test_accounts:
        print(json.dumps(account, indent=2, sort_keys=True))


def summarize_payment_db(payment_db):
    print_section("PAYMENT DB SUMMARY")

    if not isinstance(payment_db, list) or not payment_db:
        print("No payment records found.")
        return

    print("Total payment records:", len(payment_db))

    by_purchase_type = Counter()
    by_verified = Counter()
    by_receipt_approved = Counter()
    by_account = Counter()

    unsupported_purchase_type = []
    verified_unsupported = []
    receipt_not_approved = []
    local_validation_records = []
    moneris_records = []

    for record in payment_db:
        if not isinstance(record, dict):
            continue

        account_email = record.get("account_email")
        purchase_type = str(record.get("purchase_type") or "")
        verified = record.get("verified")
        receipt_approved = record.get("receipt_approved")
        source = record.get("verification_source")

        by_purchase_type[purchase_type] += 1
        by_verified[str(verified)] += 1
        by_receipt_approved[str(receipt_approved)] += 1
        by_account[str(account_email)] += 1

        summary = {
            "payment_id": record.get("payment_id"),
            "account_email": account_email,
            "purchase_type": purchase_type,
            "verified": verified,
            "receipt_request_ok": record.get("receipt_request_ok"),
            "receipt_approved": receipt_approved,
            "verification_source": source,
            "verification_reason": record.get("verification_reason"),
            "ticket_reference": record.get("ticket_reference"),
            "created_at": record.get("created_at"),
        }

        if purchase_type not in ALLOWED_PURCHASE_TYPES:
            unsupported_purchase_type.append(summary)

        if verified is True and purchase_type not in ALLOWED_PURCHASE_TYPES:
            verified_unsupported.append(summary)

        if receipt_approved is False:
            receipt_not_approved.append(summary)

        if source == "local_validation":
            local_validation_records.append(summary)

        if source == "moneris_receipt_request":
            moneris_records.append(summary)

    print("\nPurchase type counts:")
    for key, value in by_purchase_type.most_common():
        print(f"  {key}: {value}")

    print("\nVerified counts:")
    for key, value in by_verified.most_common():
        print(f"  {key}: {value}")

    print("\nReceipt approved counts:")
    for key, value in by_receipt_approved.most_common():
        print(f"  {key}: {value}")

    print("\nPayment records by account:")
    for key, value in by_account.most_common():
        print(f"  {key}: {value}")

    print("\nUnsupported purchase_type records:")
    if not unsupported_purchase_type:
        print("  None")
    for row in unsupported_purchase_type:
        print(json.dumps(row, indent=2, sort_keys=True))

    print("\nVerified records with unsupported purchase_type:")
    if not verified_unsupported:
        print("  None")
    for row in verified_unsupported:
        print(json.dumps(row, indent=2, sort_keys=True))

    print("\nReceipt not approved / blocked payment records:")
    if not receipt_not_approved:
        print("  None")
    for row in receipt_not_approved:
        print(json.dumps(row, indent=2, sort_keys=True))

    print("\nLocal validation payment records:")
    if not local_validation_records:
        print("  None")
    for row in local_validation_records:
        print(json.dumps(row, indent=2, sort_keys=True))

    print("\nRecent Moneris receipt records:")
    if not moneris_records:
        print("  None")
    for row in moneris_records[-10:]:
        print(json.dumps(row, indent=2, sort_keys=True))


def summarize_jsonl(name, rows):
    print_section(f"{name} SUMMARY")

    if not rows:
        print("No records found.")
        return

    print("Total records:", len(rows))

    parse_errors = [row for row in rows if row.get("_parse_error")]
    if parse_errors:
        print("\nParse errors:")
        for row in parse_errors[-10:]:
            print(json.dumps(row, indent=2, sort_keys=True))

    by_status = Counter(str(row.get("status")) for row in rows if isinstance(row, dict))
    by_email = Counter(str(row.get("email")) for row in rows if isinstance(row, dict) and row.get("email"))
    by_plan = Counter(str(row.get("plan")) for row in rows if isinstance(row, dict) and row.get("plan"))

    print("\nStatus counts:")
    for key, value in by_status.most_common():
        print(f"  {key}: {value}")

    print("\nPlan counts:")
    for key, value in by_plan.most_common():
        print(f"  {key}: {value}")

    print("\nTop emails:")
    for key, value in by_email.most_common(20):
        print(f"  {key}: {value}")

    print("\nRecent records:")
    for row in rows[-10:]:
        safe = {
            "timestamp": row.get("timestamp"),
            "order_no": row.get("order_no"),
            "email": row.get("email"),
            "plan": row.get("plan"),
            "amount": row.get("amount"),
            "status": row.get("status"),
            "moneris_env": row.get("moneris_env"),
        }

        if row.get("ticket"):
            safe["ticket_suffix"] = ticket_suffix(row.get("ticket"))

        response = row.get("moneris_response")
        if isinstance(response, dict):
            ticket = (((response.get("response") or {}).get("ticket")) or "")
            success = (((response.get("response") or {}).get("success")) or "")
            error = (((response.get("response") or {}).get("error")) or "")
            safe["moneris_success"] = success
            safe["moneris_ticket_suffix"] = ticket_suffix(ticket)
            safe["moneris_error"] = error

        print(json.dumps(safe, indent=2, sort_keys=True))


def print_recommendations(usage_db, payment_db):
    print_section("AUDIT RECOMMENDATIONS")

    recommendations = []

    if isinstance(payment_db, list):
        unsupported_verified = [
            r for r in payment_db
            if isinstance(r, dict)
            and r.get("verified") is True
            and str(r.get("purchase_type") or "") not in ALLOWED_PURCHASE_TYPES
        ]

        if unsupported_verified:
            recommendations.append(
                "Review verified payment records with unsupported purchase_type. "
                "These are historical test artifacts and should not be mixed with real customer data."
            )

        local_validation = [
            r for r in payment_db
            if isinstance(r, dict)
            and r.get("verification_source") == "local_validation"
        ]

        if local_validation:
            recommendations.append(
                "Review local_validation payment records. These should remain internal QA/test only."
            )

    if isinstance(usage_db, dict):
        local_notes = [
            email for email, record in usage_db.items()
            if isinstance(record, dict) and record.get("local_test_note")
        ]

        if local_notes:
            recommendations.append(
                "Review usage records with local_test_note. These are manually simulated/test records."
            )

    if not recommendations:
        recommendations.append("No obvious cleanup concerns detected by this read-only audit.")

    for idx, item in enumerate(recommendations, 1):
        print(f"{idx}. {item}")

    print("\nREAD-ONLY CONFIRMATION:")
    print("This script did not modify, delete, archive, migrate, or repair any file.")


def main():
    print_section("ASTRAA RUNTIME DATA AUDIT")
    print("Audit time:", datetime.utcnow().isoformat() + "Z")
    print("Working directory:", str(Path.cwd()))
    print("Mode: READ ONLY")

    usage_db = load_json(USAGE_DB, {})
    payment_db = load_json(PAYMENT_DB, [])
    preloads = load_jsonl(PRELOADS_JSONL)
    payments = load_jsonl(PAYMENTS_JSONL)

    summarize_usage_db(usage_db)
    summarize_payment_db(payment_db)
    summarize_jsonl("PRELOADS JSONL", preloads)
    summarize_jsonl("PAYMENTS JSONL", payments)
    print_recommendations(usage_db, payment_db)


if __name__ == "__main__":
    main()
