from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from decimal import Decimal, InvalidOperation
from datetime import datetime
import os
import json
import uuid
import requests

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv(override=True)

app = Flask(__name__)
CORS(app)

# -------------------------------------------------
# Astraa API security
# -------------------------------------------------
API_KEY = os.getenv("ASTRAA_API_KEY", "astraa_secure")

# -------------------------------------------------
# Moneris production credentials
# -------------------------------------------------
MONERIS_STORE_ID = os.getenv("MONERIS_STORE_ID", "")
MONERIS_API_TOKEN = os.getenv("MONERIS_API_TOKEN", "")
MONERIS_CHECKOUT_ID = os.getenv("MONERIS_CHECKOUT_ID", "")
MONERIS_ENV = os.getenv("MONERIS_ENV", "prod").lower()

# -------------------------------------------------
# Optional safe testing override
# If you want to charge a small production test amount,
# set ASTRAA_TEST_AMOUNT=2.00 in .env
# If empty, real plan prices are used.
# -------------------------------------------------
ASTRAA_TEST_AMOUNT = os.getenv("ASTRAA_TEST_AMOUNT", "").strip()

# -------------------------------------------------
# Files
# -------------------------------------------------
PAYMENTS_FILE = "payments.jsonl"
PRELOADS_FILE = "preloads.jsonl"
RECEIPTS_FILE = "receipts.jsonl"

# -------------------------------------------------
# Plan pricing
# -------------------------------------------------
PLAN_PRICES = {
    "basic": "39.00",
    "professional": "99.00"
}

PLAN_LABELS = {
    "basic": "Astraa Basic",
    "professional": "Astraa Professional"
}

# -------------------------------------------------
# Moneris endpoints
# -------------------------------------------------
if MONERIS_ENV == "prod":
    MONERIS_REQUEST_URL = "https://gateway.moneris.com/chkt/request/request.php"
    MONERIS_ENV_VALUE = "prod"
else:
    MONERIS_REQUEST_URL = "https://gatewayt.moneris.com/chkt/request/request.php"
    MONERIS_ENV_VALUE = "qa"


# -------------------------------------------------
# Utility helpers
# -------------------------------------------------
def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def append_jsonl(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def authorized(req):
    return req.headers.get("X-API-KEY") == API_KEY


def safe_amount(value):
    """
    Validate and normalize amount to Moneris-style decimal string.
    Example: 39.00
    """
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
        if amount <= 0:
            return None
        return f"{amount:.2f}"
    except (InvalidOperation, ValueError):
        return None


def get_plan_amount(plan):
    """
    Server-side plan pricing.
    The frontend may send amount, but backend controls final amount.
    """
    normalized_plan = (plan or "professional").lower().strip()

    if normalized_plan not in PLAN_PRICES:
        normalized_plan = "professional"

    if ASTRAA_TEST_AMOUNT:
        test_amount = safe_amount(ASTRAA_TEST_AMOUNT)
        if test_amount:
            return normalized_plan, test_amount

    return normalized_plan, PLAN_PRICES[normalized_plan]


def get_plan_label(plan):
    return PLAN_LABELS.get(plan, "Astraa Professional")


def config_status():
    return {
        "store_id_loaded": bool(MONERIS_STORE_ID),
        "api_token_loaded": bool(MONERIS_API_TOKEN),
        "checkout_id_loaded": bool(MONERIS_CHECKOUT_ID),
        "moneris_env": MONERIS_ENV_VALUE,
        "moneris_url": MONERIS_REQUEST_URL,
        "test_amount_override": ASTRAA_TEST_AMOUNT if ASTRAA_TEST_AMOUNT else None
    }


# -------------------------------------------------
# Startup debug
# -------------------------------------------------
print("======================================")
print("Astraa API starting")
print("MONERIS_STORE_ID loaded:", bool(MONERIS_STORE_ID))
print("MONERIS_API_TOKEN loaded:", bool(MONERIS_API_TOKEN))
print("MONERIS_CHECKOUT_ID loaded:", bool(MONERIS_CHECKOUT_ID))
print("MONERIS_ENV:", MONERIS_ENV_VALUE)
print("MONERIS URL:", MONERIS_REQUEST_URL)
print("ASTRAA_TEST_AMOUNT:", ASTRAA_TEST_AMOUNT if ASTRAA_TEST_AMOUNT else "not set")
print("======================================")


# -------------------------------------------------
# Health
# -------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Astraa API running",
        "config": config_status()
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": now_iso(),
        "config": config_status()
    })


# -------------------------------------------------
# Moneris Checkout Preload
# -------------------------------------------------
@app.route("/preload", methods=["POST"])
def preload():
    if not authorized(request):
        return jsonify({
            "status": "error",
            "message": "unauthorized"
        }), 403

    if not MONERIS_STORE_ID or not MONERIS_API_TOKEN or not MONERIS_CHECKOUT_ID:
        return jsonify({
            "response": {
                "success": "false",
                "error": {
                    "config": {
                        "data": "Missing MONERIS_STORE_ID, MONERIS_API_TOKEN, or MONERIS_CHECKOUT_ID"
                    }
                }
            }
        }), 500

    data = request.json or {}

    email = (data.get("email") or "").strip()
    requested_plan = (data.get("plan") or "professional").strip().lower()

    plan, amount = get_plan_amount(requested_plan)
    plan_label = get_plan_label(plan)

    order_no = "ASTRAA-" + datetime.utcnow().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6].upper()

    payload = {
        "store_id": MONERIS_STORE_ID,
        "api_token": MONERIS_API_TOKEN,
        "checkout_id": MONERIS_CHECKOUT_ID,
        "txn_total": amount,
        "environment": MONERIS_ENV_VALUE,
        "action": "preload",
        "order_no": order_no,
        "cust_id": email if email else order_no,
        "dynamic_descriptor": "ASTRAA",
        "language": "en",
        "contact_details": {
            "first_name": "Astraa",
            "last_name": "Customer",
            "email": email if email else "customer@astraasystems.com",
            "phone": ""
        },
        "cart": {
            "items": [
                {
                    "description": plan_label,
                    "product_code": plan,
                    "unit_cost": amount,
                    "quantity": "1"
                }
            ],
            "subtotal": amount
        }
    }

    preload_record = {
        "timestamp": now_iso(),
        "order_no": order_no,
        "email": email,
        "plan": plan,
        "amount": amount,
        "moneris_env": MONERIS_ENV_VALUE,
        "status": "initiated"
    }

    append_jsonl(PRELOADS_FILE, preload_record)

    try:
        response = requests.post(
            MONERIS_REQUEST_URL,
            json=payload,
            timeout=30
        )

        raw_text = response.text

        print("MONERIS PRELOAD HTTP STATUS:", response.status_code)
        print("MONERIS PRELOAD RAW:", raw_text)

        try:
            moneris_data = response.json()
        except Exception:
            error_payload = {
                "response": {
                    "success": "false",
                    "error": {
                        "gateway": {
                            "data": "Moneris returned non-JSON response",
                            "http_status": response.status_code,
                            "raw": raw_text
                        }
                    }
                }
            }

            preload_record["status"] = "failed_non_json"
            preload_record["raw_response"] = raw_text
            append_jsonl(PRELOADS_FILE, preload_record)

            return jsonify(error_payload), 500

        preload_record["status"] = "response_received"
        preload_record["moneris_response"] = moneris_data
        append_jsonl(PRELOADS_FILE, preload_record)

        # Log payment session if ticket received
        if (
            isinstance(moneris_data, dict)
            and moneris_data.get("response", {}).get("success") == "true"
            and moneris_data.get("response", {}).get("ticket")
        ):
            payment_record = {
                "timestamp": now_iso(),
                "order_no": order_no,
                "email": email,
                "plan": plan,
                "amount": amount,
                "ticket": moneris_data["response"]["ticket"],
                "status": "ticket_created"
            }
            append_jsonl(PAYMENTS_FILE, payment_record)

        return jsonify(moneris_data)

    except requests.exceptions.RequestException as e:
        error_payload = {
            "response": {
                "success": "false",
                "error": {
                    "exception": {
                        "data": str(e)
                    }
                }
            }
        }

        preload_record["status"] = "request_exception"
        preload_record["error"] = str(e)
        append_jsonl(PRELOADS_FILE, preload_record)

        return jsonify(error_payload), 500


# -------------------------------------------------
# Moneris Checkout Receipt Request
# Used after payment_complete callback later.
# -------------------------------------------------
@app.route("/receipt", methods=["POST"])
def receipt():
    if not authorized(request):
        return jsonify({
            "status": "error",
            "message": "unauthorized"
        }), 403

    data = request.json or {}
    ticket = (data.get("ticket") or "").strip()

    if not ticket:
        return jsonify({
            "response": {
                "success": "false",
                "error": {
                    "ticket": {
                        "data": "Missing ticket"
                    }
                }
            }
        }), 400

    if not MONERIS_STORE_ID or not MONERIS_API_TOKEN or not MONERIS_CHECKOUT_ID:
        return jsonify({
            "response": {
                "success": "false",
                "error": {
                    "config": {
                        "data": "Missing MONERIS_STORE_ID, MONERIS_API_TOKEN, or MONERIS_CHECKOUT_ID"
                    }
                }
            }
        }), 500

    payload = {
        "store_id": MONERIS_STORE_ID,
        "api_token": MONERIS_API_TOKEN,
        "checkout_id": MONERIS_CHECKOUT_ID,
        "ticket": ticket,
        "environment": MONERIS_ENV_VALUE,
        "action": "receipt"
    }

    receipt_record = {
        "timestamp": now_iso(),
        "ticket": ticket,
        "status": "initiated"
    }

    append_jsonl(RECEIPTS_FILE, receipt_record)

    try:
        response = requests.post(
            MONERIS_REQUEST_URL,
            json=payload,
            timeout=30
        )

        raw_text = response.text

        print("MONERIS RECEIPT HTTP STATUS:", response.status_code)
        print("MONERIS RECEIPT RAW:", raw_text)

        try:
            moneris_data = response.json()
        except Exception:
            receipt_record["status"] = "failed_non_json"
            receipt_record["raw_response"] = raw_text
            append_jsonl(RECEIPTS_FILE, receipt_record)

            return jsonify({
                "response": {
                    "success": "false",
                    "error": {
                        "gateway": {
                            "data": "Moneris returned non-JSON response",
                            "http_status": response.status_code,
                            "raw": raw_text
                        }
                    }
                }
            }), 500

        receipt_record["status"] = "response_received"
        receipt_record["moneris_response"] = moneris_data
        append_jsonl(RECEIPTS_FILE, receipt_record)

        return jsonify(moneris_data)

    except requests.exceptions.RequestException as e:
        receipt_record["status"] = "request_exception"
        receipt_record["error"] = str(e)
        append_jsonl(RECEIPTS_FILE, receipt_record)

        return jsonify({
            "response": {
                "success": "false",
                "error": {
                    "exception": {
                        "data": str(e)
                    }
                }
            }
        }), 500


# -------------------------------------------------
# Optional simple lead endpoint for later use
# -------------------------------------------------
@app.route("/lead", methods=["POST"])
def lead():
    if not authorized(request):
        return jsonify({
            "status": "error",
            "message": "unauthorized"
        }), 403

    data = request.json or {}

    record = {
        "timestamp": now_iso(),
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "company": data.get("company", ""),
        "request_type": data.get("request_type", ""),
        "message": data.get("message", "")
    }

    append_jsonl("leads.jsonl", record)

    return jsonify({
        "status": "ok",
        "message": "Lead captured"
    })


# -------------------------------------------------
# Run server
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
