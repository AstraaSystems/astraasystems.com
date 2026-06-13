from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)

API_KEY = "astraa_secure"
LEADS_FILE = "leads.jsonl"

# ---------- MONERIS CONFIG ----------
# Fill these with your actual values or export them as environment variables.
MONERIS_STORE_ID = os.getenv("MONERIS_STORE_ID", "PUT_YOUR_STORE_ID_HERE")
MONERIS_API_TOKEN = os.getenv("MONERIS_API_TOKEN", "PUT_YOUR_API_TOKEN_HERE")
MONERIS_WEBSITE_TOKEN = os.getenv("MONERIS_WEBSITE_TOKEN", "PUT_YOUR_WEBSITE_TOKEN_HERE")

# ---------- SMTP CONFIG ----------
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
LEAD_NOTIFY_EMAIL = os.getenv("LEAD_NOTIFY_EMAIL", "contact@astraasystems.com")


def authorized(req):
    return req.headers.get("X-API-KEY") == API_KEY


def append_jsonl(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def send_email(subject, body, to_email):
    if not SMTP_USER or not SMTP_PASS:
        return {"status": "skipped", "reason": "smtp not configured"}

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    return {"status": "sent"}


@app.route("/", methods=["GET"])
def home():
    return "Astraa API is running"


# ---------- ESTIMATOR ----------
@app.route("/estimate", methods=["POST"])
def estimate():
    if not authorized(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.json or {}

    sqft = float(data.get("sqft", 10000))
    material = float(data.get("material", 1.1))
    labor = float(data.get("labor", 1.05))
    complexity = float(data.get("complexity", 0.8))

    base = sqft * 400
    estimate_value = base * material * labor * complexity

    return jsonify({
        "base_estimate": estimate_value,
        "confidence": 0.92,
        "risk": "Moderate"
    })


# ---------- LEAD CAPTURE ----------
@app.route("/lead", methods=["POST"])
def lead():
    if not authorized(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.json or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    estimate_context = data.get("estimate_context", {})

    if not name or not email:
        return jsonify({"error": "name and email required"}), 400

    record = {
        "name": name,
        "email": email,
        "estimate_context": estimate_context,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    append_jsonl(LEADS_FILE, record)

    email_body = f"""
New Astraa lead captured

Name: {name}
Email: {email}
Estimate Context:
{json.dumps(estimate_context, indent=2)}

Timestamp: {record["timestamp"]}
"""
    email_result = send_email(
        subject="New Astraa Lead Captured",
        body=email_body,
        to_email=LEAD_NOTIFY_EMAIL
    )

    return jsonify({
        "status": "ok",
        "message": "Lead captured successfully",
        "email_notification": email_result
    })


# ---------- MONERIS-READY PAYMENT CONFIG ----------
@app.route("/payment/config", methods=["GET"])
def payment_config():
    if MONERIS_STORE_ID.startswith("PUT_") or MONERIS_API_TOKEN.startswith("PUT_") or MONERIS_WEBSITE_TOKEN.startswith("PUT_"):
        return jsonify({
            "status": "incomplete",
            "message": "Moneris credentials not configured yet"
        })

    return jsonify({
        "status": "ready",
        "store_id": MONERIS_STORE_ID,
        "website_token": MONERIS_WEBSITE_TOKEN
    })


# ---------- PAYMENT ENTRY POINT ----------
@app.route("/pay", methods=["POST"])
def pay():
    if not authorized(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.json or {}
    email = data.get("email", "").strip()
    plan = data.get("plan", "trial")

    # NOTE:
    # This route is "Moneris-ready", but not charging yet.
    # It validates config and gives back the values needed
    # for the next integration step (Hosted Checkout/Hosted Tokenization).

    if MONERIS_STORE_ID.startswith("PUT_") or MONERIS_API_TOKEN.startswith("PUT_") or MONERIS_WEBSITE_TOKEN.startswith("PUT_"):
        return jsonify({
            "status": "incomplete",
            "message": "Moneris is not fully configured yet"
        }), 400

    record = {
        "email": email,
        "plan": plan,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payment_provider": "Moneris",
        "status": "initiated"
    }

    append_jsonl("payments.jsonl", record)

    # EMAIL NOTIFY
    send_email(
        subject="Astraa Trial Payment Started",
        body=f"Payment initiated for {email} on plan: {plan}",
        to_email=LEAD_NOTIFY_EMAIL
    )

    return jsonify({
        "status": "ready",
        "message": "Payment route is active and Moneris credentials are loaded",
        "moneris": {
            "store_id": MONERIS_STORE_ID,
            "website_token": MONERIS_WEBSITE_TOKEN
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
