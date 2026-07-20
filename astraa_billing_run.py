#!/usr/bin/env python3
"""ASTRAA BILLING SCHEDULER — Block 4. Runs daily via cron. Catch-up safe."""
import os, sys, json
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

for line in open(".env", encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import importlib.util
spec = importlib.util.spec_from_file_location("astraa_api", os.path.join(BASE_DIR, "api.py"))
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

LOG = os.path.join("astraa_data", "billing_scheduler.log")

def log(msg):
    line = datetime.now(timezone.utc).isoformat() + "  " + msg
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def today_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def add_month(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return (d + timedelta(days=30)).strftime("%Y-%m-%d")

def _flip_account(email, status):
    try:
        key = api.astraa_account_key(email)
    except Exception:
        key = email.strip().lower()
    udb = api.astraa_load_usage_db()
    rec = udb.get(key) or udb.get(email) or udb.get(email.strip().lower())
    if rec:
        rec["payment_status"] = status
        rec["subscription_status"] = status
        rec["updated_at"] = datetime.now(timezone.utc).isoformat()
        udb[key if key in udb else email] = rec
        api.astraa_save_usage_db(udb)

def run():
    log("=== Billing run start ===")
    subs = api.astraa_load_subs_db()
    if not subs:
        log("No subscriptions on file. Done.")
        return
    today = today_str()
    charged = failed = skipped = 0
    for key, rec in list(subs.items()):
        if rec.get("status") != "active":
            skipped += 1; continue
        next_bill = rec.get("next_bill_date")
        if not next_bill or next_bill > today:
            skipped += 1; continue
        email = rec.get("email", key); product = rec.get("product", "")
        amount = rec.get("amount_cents"); pmid = rec.get("payment_method_id")
        guard = 0
        while next_bill and next_bill <= today and guard < 24:
            guard += 1
            log(f"Charging {email} ({product}) ${amount/100:.2f} due {next_bill}")
            ok, result = api.astraa_charge_payment_method(pmid, amount, email, product, "SUBSEQUENT")
            now_iso = datetime.now(timezone.utc).isoformat()
            if ok:
                charged += 1
                rec["last_charge_at"] = now_iso
                rec["last_charge_order"] = result.get("orderId")
                rec["charge_count"] = rec.get("charge_count", 0) + 1
                next_bill = add_month(next_bill)
                rec["next_bill_date"] = next_bill
                rec.setdefault("history", []).append({"at": now_iso, "type": "recurring_charge",
                    "order": result.get("orderId"), "status": result.get("paymentStatus")})
                rec["status"] = "active"
                log(f"  SUCCESS order={result.get('orderId')} next={next_bill}")
                try: _flip_account(email, "active")
                except Exception as e: log(f"  (usage db update failed: {e})")
            else:
                failed += 1
                rec["status"] = "past_due"
                rec["last_failure_at"] = now_iso
                rec.setdefault("history", []).append({"at": now_iso, "type": "charge_failed", "error": result})
                log(f"  FAILED {email}: {result}")
                try: _flip_account(email, "past_due")
                except Exception as e: log(f"  (usage db update failed: {e})")
                break
        subs[key] = rec
    api.astraa_save_subs_db(subs)
    log(f"=== Done. charged={charged} failed={failed} skipped={skipped} ===")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log(f"FATAL: {e}")
        sys.exit(1)
