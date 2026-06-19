#!/usr/bin/env python3
"""
Astraa Runtime Cleanup Plan

READ-ONLY SCRIPT.
This script does not delete, modify, write, archive, migrate, or repair data.

Purpose:
- Build a cleanup/migration plan from local runtime data.
- Classify records as:
  - KEEP_AS_PROOF
  - ARCHIVE_LATER
  - DO_NOT_MIGRATE
  - MANUAL_REVIEW
- Help prepare public-launch data separation safely.

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
from datetime import datetime, timezone


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


KNOWN_PROOF_EMAILS = {
    "approved.live.test@astraasystems.com",
    "astraa.live.test@astraasystems.com",
}


TEST_MARKERS = [
    "test",
    "approved",
    "qa",
    "simulation",
    "malicious-change",
    "keshanth.sivayo@gmail.com",
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
            rows.append(json.loads(line))
        except Exception as exc:
            rows.append({
                "_parse_error": str(exc),
                "_line_number": idx,
                "_raw": line[:500],
            })
    return rows


def is_test_email(email):
    email_l = str(email or "").lower()
    return any(marker in email_l for marker in TEST_MARKERS)


def ticket_suffix(value):
    value = str(value or "")
    return value[-12:] if value else ""


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def classify_usage(email, record):
    email_l = str(email or "").lower()
    status = str(record.get("payment_status") or "")
    sub_status = str(record.get("subscription_status") or "")
    local_note = record.get("local_test_note")

    reasons = []

    if email_l in KNOWN_PROOF_EMAILS and status == "active" and sub_status == "active":
        reasons.append("Known QA/proof account with active payment/subscription.")
        return "KEEP_AS_PROOF", reasons

    if local_note:
        reasons.append("Contains local_test_note/manual simulation marker.")
        return "DO_NOT_MIGRATE", reasons

    if "malicious-change" in email_l:
        reasons.append("Security test account for payload hijack protection.")
        return "DO_NOT_MIGRATE", reasons

    if is_test_email(email):
        reasons.append("Likely internal QA/test account.")
        return "ARCHIVE_LATER", reasons

    if status in ["inactive", "pending"] or sub_status in ["inactive", "pending"]:
        reasons.append("Inactive or pending local runtime account.")
        return "MANUAL_REVIEW", reasons

    if status == "trial" or sub_status == "trial":
        reasons.append("Trial local runtime account.")
        return "MANUAL_REVIEW", reasons

    if status == "active" or sub_status == "active":
        reasons.append("Active account; verify whether it is real customer or QA before migration.")
        return "MANUAL_REVIEW", reasons

    reasons.append("Unclassified usage record.")
    return "MANUAL_REVIEW", reasons


def classify_payment(record):
    account_email = str(record.get("account_email") or "").lower()
    purchase_type = str(record.get("purchase_type") or "")
    verified = record.get("verified")
    receipt_approved = record.get("receipt_approved")
    source = record.get("verification_source")
    ticket_ref = str(record.get("ticket_reference") or "")

    reasons = []

    if purchase_type not in ALLOWED_PURCHASE_TYPES:
        reasons.append("Unsupported purchase_type.")
        if verified is True:
            reasons.append("Verified=true with unsupported purchase_type; historical test artifact.")
        return "DO_NOT_MIGRATE", reasons

    if source == "local_validation":
        reasons.append("Local validation record; not Moneris-approved proof.")
        return "DO_NOT_MIGRATE", reasons

    if "_TICKET_HERE" in ticket_ref or "TICKET_HERE" in ticket_ref:
        reasons.append("Placeholder ticket reference.")
        return "DO_NOT_MIGRATE", reasons

    if account_email in KNOWN_PROOF_EMAILS and verified is True and receipt_approved is True:
        reasons.append("Known successful Moneris proof record.")
        return "KEEP_AS_PROOF", reasons

    if receipt_approved is False or verified is False:
        reasons.append("Failed/declined/unverified payment proof; useful as QA evidence.")
        return "ARCHIVE_LATER", reasons

    if is_test_email(account_email):
        reasons.append("Likely internal QA/test payment record.")
        return "ARCHIVE_LATER", reasons

    if verified is True:
        reasons.append("Verified payment; manually confirm whether customer or QA before migration.")
        return "MANUAL_REVIEW", reasons

    reasons.append("Unclassified payment record.")
    return "MANUAL_REVIEW", reasons


def plan_usage(usage_db):
    section("USAGE CLEANUP PLAN")

    buckets = defaultdict(list)

    if not isinstance(usage_db, dict):
        print("Usage DB is not an object.")
        return buckets

    for email, record in usage_db.items():
        if not isinstance(record, dict):
            continue

        classification, reasons = classify_usage(email, record)

        buckets[classification].append({
            "email": email,
            "account_id": record.get("account_id"),
            "selected_plan": record.get("selected_plan") or record.get("plan"),
            "payment_status": record.get("payment_status"),
            "subscription_status": record.get("subscription_status"),
            "estimate_limit": record.get("estimate_limit"),
            "estimate_used": record.get("estimate_used"),
            "extra_estimate_credits_total": record.get("extra_estimate_credits_total"),
            "extra_estimate_credits_used": record.get("extra_estimate_credits_used"),
            "reasons": reasons,
        })

    for classification in ["KEEP_AS_PROOF", "ARCHIVE_LATER", "DO_NOT_MIGRATE", "MANUAL_REVIEW"]:
        rows = buckets.get(classification, [])
        print(f"\n{classification}: {len(rows)}")
        for row in rows:
            print(json.dumps(row, indent=2, sort_keys=True))

    return buckets


def plan_payments(payment_db):
    section("PAYMENT CLEANUP PLAN")

    buckets = defaultdict(list)

    if not isinstance(payment_db, list):
        print("Payment DB is not a list.")
        return buckets

    for record in payment_db:
        if not isinstance(record, dict):
            continue

        classification, reasons = classify_payment(record)

        buckets[classification].append({
            "payment_id": record.get("payment_id"),
            "account_email": record.get("account_email"),
            "purchase_type": record.get("purchase_type"),
            "verified": record.get("verified"),
            "receipt_request_ok": record.get("receipt_request_ok"),
            "receipt_approved": record.get("receipt_approved"),
            "verification_source": record.get("verification_source"),
            "verification_reason": record.get("verification_reason"),
            "ticket_reference": record.get("ticket_reference"),
            "created_at": record.get("created_at"),
            "reasons": reasons,
        })

    for classification in ["KEEP_AS_PROOF", "ARCHIVE_LATER", "DO_NOT_MIGRATE", "MANUAL_REVIEW"]:
        rows = buckets.get(classification, [])
        print(f"\n{classification}: {len(rows)}")
        for row in rows:
            print(json.dumps(row, indent=2, sort_keys=True))

    return buckets


def plan_jsonl(name, rows):
    section(f"{name} CLEANUP PLAN")

    print("Total records:", len(rows))

    by_email = Counter(str(row.get("email")) for row in rows if isinstance(row, dict) and row.get("email"))
    by_status = Counter(str(row.get("status")) for row in rows if isinstance(row, dict))

    print("\nStatus counts:")
    for key, value in by_status.most_common():
        print(f"  {key}: {value}")

    print("\nTop emails:")
    for key, value in by_email.most_common(20):
        print(f"  {key}: {value}")

    print("\nPlanning guidance:")
    print("- KEEP_AS_PROOF: selected recent approved/declined proof records only.")
    print("- ARCHIVE_LATER: full JSONL history may be archived outside public production data.")
    print("- DO_NOT_MIGRATE: placeholder/error/security-test records should not become customer records.")


def print_summary(usage_buckets, payment_buckets):
    section("CLEANUP PLAN SUMMARY")

    print("Usage classifications:")
    for key in ["KEEP_AS_PROOF", "ARCHIVE_LATER", "DO_NOT_MIGRATE", "MANUAL_REVIEW"]:
        print(f"  {key}: {len(usage_buckets.get(key, []))}")

    print("\nPayment classifications:")
    for key in ["KEEP_AS_PROOF", "ARCHIVE_LATER", "DO_NOT_MIGRATE", "MANUAL_REVIEW"]:
        print(f"  {key}: {len(payment_buckets.get(key, []))}")

    print("\nRecommended next action:")
    print("1. Keep this as read-only planning output.")
    print("2. Do not delete or migrate records yet.")
    print("3. Next create an archive/export script that writes a separate archive copy, but still does not delete.")
    print("4. Only after archive verification should a cleanup/migration script be considered.")

    print("\nREAD-ONLY CONFIRMATION:")
    print("This script did not modify, delete, archive, migrate, or repair any file.")


def main():
    section("ASTRAA RUNTIME CLEANUP PLAN")
    print("Plan time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", str(Path.cwd()))
    print("Mode: READ ONLY")

    usage_db = load_json(USAGE_DB, {})
    payment_db = load_json(PAYMENT_DB, [])
    preloads = load_jsonl(PRELOADS_JSONL)
    payments = load_jsonl(PAYMENTS_JSONL)

    usage_buckets = plan_usage(usage_db)
    payment_buckets = plan_payments(payment_db)
    plan_jsonl("PRELOADS JSONL", preloads)
    plan_jsonl("PAYMENTS JSONL", payments)
    print_summary(usage_buckets, payment_buckets)


if __name__ == "__main__":
    main()
