"""
Astraa Lead Capture Automation

Inbound, consent-based lead capture for Astraa Systems.

Purpose:
- Capture guided trial / Workspace lead requests.
- Store consent text, timestamp, source page, and lead details.
- Score leads by product interest and business fit.
- Queue a compliant confirmation/follow-up message.
- Generate sales-channel signals for deciding which Astraa products to bring live next.

Does NOT:
- scrape emails
- send unsolicited messages
- mass-email prospects
- auto-launch paid SaaS modules
- run payments
- unlock customer access
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, request
from astraa_arka_bridge import send_astraa_event_to_arka


astraa_leads = Blueprint("astraa_leads", __name__)

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LEADS_FILE = DATA_DIR / "astraa_leads.jsonl"
EMAIL_QUEUE_FILE = DATA_DIR / "astraa_email_queue.jsonl"
SALES_SIGNAL_FILE = DATA_DIR / "astraa_sales_signal.json"

CONSENT_TEXT = (
    "I agree that Astraa Systems may contact me about my trial request, "
    "onboarding, and related Astraa services. I can unsubscribe or ask to stop "
    "receiving messages at any time."
)

ALLOWED_INTERESTS = {
    "estimator",
    "finance",
    "operations",
    "workspace",
    "full workspace",
    "support",
    "custom",
}

HIGH_VALUE_INDUSTRIES = {
    "construction",
    "contractor",
    "renovation",
    "landscaping",
    "cleaning",
    "logistics",
    "franchise",
    "non-profit",
    "nonprofit",
    "consulting",
    "small business",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def normalize(value: Any) -> str:
    return str(value or "").strip()


def lower(value: Any) -> str:
    return normalize(value).lower()


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    ensure_data_dir()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def score_lead(lead: dict[str, Any]) -> int:
    score = 0

    email = lower(lead.get("email"))
    business_name = lower(lead.get("business_name"))
    phone = lower(lead.get("phone"))
    industry = lower(lead.get("industry"))
    interest = lower(lead.get("tool_interest"))
    challenge = lower(lead.get("current_challenge"))
    business_size = lower(lead.get("business_size"))

    if email:
        score += 10
    if business_name:
        score += 10
    if phone:
        score += 5
    if any(item in industry for item in HIGH_VALUE_INDUSTRIES):
        score += 15
    if interest in {"finance", "operations", "workspace", "full workspace"}:
        score += 15
    elif interest == "estimator":
        score += 10
    if challenge and len(challenge) >= 25:
        score += 15
    if any(token in business_size for token in ["2", "3", "5", "10", "team", "crew", "staff", "employees"]):
        score += 10

    return min(score, 100)


def lead_status(score: int) -> str:
    if score >= 70:
        return "Qualified"
    if score >= 45:
        return "Warm"
    return "New"


def next_action(score: int, interest: str) -> str:
    if score >= 70:
        return f"Offer guided Astraa Workspace setup focused on {interest or 'Workspace'}."
    if score >= 45:
        return "Send clarification follow-up and ask which tool should be configured first."
    return "Send confirmation and monitor for reply."


def build_confirmation_email(lead: dict[str, Any]) -> dict[str, Any]:
    name = lead.get("name") or "there"
    business_name = lead.get("business_name") or "your business"
    interest = lead.get("tool_interest") or "Astraa Workspace"
    email = lead.get("email")

    subject = "Your Astraa Workspace trial request was received"

    body = f"""Hi {name},

Thanks for requesting Astraa Workspace access for {business_name}.

We received your interest in: {interest}.

Astraa Systems will review your setup request and follow up with the best guided trial path for Estimator, Finance, Operations, or full Workspace access.

Astraa Systems
Connected business tools

You can reply to update your request. If you no longer want messages from Astraa, reply "unsubscribe" or "stop".
"""

    return {
        "created_at": utc_now(),
        "type": "lead_confirmation",
        "to": email,
        "subject": subject,
        "body": body,
        "status": "queued_manual_send",
        "casl_note": "Inbound lead confirmation; includes sender identity and unsubscribe/stop wording.",
    }


def update_sales_signal() -> dict[str, Any]:
    leads = read_jsonl(LEADS_FILE)

    counts = {
        "total_leads": len(leads),
        "qualified": 0,
        "warm": 0,
        "estimator_interest": 0,
        "finance_interest": 0,
        "operations_interest": 0,
        "workspace_interest": 0,
    }

    for lead in leads:
        status = lead.get("status")
        interest = lower(lead.get("tool_interest"))

        if status == "Qualified":
            counts["qualified"] += 1
        if status == "Warm":
            counts["warm"] += 1

        if "estimator" in interest:
            counts["estimator_interest"] += 1
        if "finance" in interest:
            counts["finance_interest"] += 1
        if "operations" in interest:
            counts["operations_interest"] += 1
        if "workspace" in interest:
            counts["workspace_interest"] += 1

    product_priority = sorted(
        [
            ("Estimator", counts["estimator_interest"]),
            ("Finance", counts["finance_interest"]),
            ("Operations", counts["operations_interest"]),
            ("Workspace", counts["workspace_interest"]),
        ],
        key=lambda item: item[1],
        reverse=True,
    )

    signal = {
        "generated_at": utc_now(),
        "counts": counts,
        "top_product_interest": product_priority,
        "sales_channel_signal": "insufficient_data",
        "recommended_next_product_focus": product_priority[0][0] if product_priority else None,
        "operator_note": "Use this as a decision signal only. Do not auto-launch paid modules without operator approval.",
    }

    if counts["qualified"] >= 3 or counts["total_leads"] >= 10:
        signal["sales_channel_signal"] = "review_for_product_activation"

    ensure_data_dir()
    SALES_SIGNAL_FILE.write_text(json.dumps(signal, indent=2, ensure_ascii=False), encoding="utf-8")
    return signal


@astraa_leads.route("/api/leads", methods=["POST"])
def create_lead():
    payload = request.get_json(silent=True) or {}

    name = normalize(payload.get("name"))
    business_name = normalize(payload.get("business_name"))
    email = normalize(payload.get("email"))
    phone = normalize(payload.get("phone"))
    province = normalize(payload.get("province"))
    industry = normalize(payload.get("industry"))
    business_size = normalize(payload.get("business_size"))
    tool_interest = normalize(payload.get("tool_interest"))
    current_challenge = normalize(payload.get("current_challenge"))
    source_page = normalize(payload.get("source_page"))
    consent_accepted = bool(payload.get("consent_accepted"))

    errors: list[str] = []

    if not name:
        errors.append("name is required")
    if not business_name:
        errors.append("business_name is required")
    if not email or "@" not in email:
        errors.append("valid email is required")
    if not tool_interest:
        errors.append("tool_interest is required")
    if not consent_accepted:
        errors.append("consent_accepted is required")

    if tool_interest and lower(tool_interest) not in ALLOWED_INTERESTS:
        # Do not block; normalize unusual interests into custom.
        tool_interest = "custom"

    if errors:
        return jsonify({
            "ok": False,
            "errors": errors,
        }), 400

    lead = {
        "created_at": utc_now(),
        "name": name,
        "business_name": business_name,
        "email": email,
        "phone": phone,
        "province": province,
        "industry": industry,
        "business_size": business_size,
        "tool_interest": tool_interest,
        "current_challenge": current_challenge,
        "source_page": source_page,
        "consent_accepted": consent_accepted,
        "consent_text": CONSENT_TEXT,
        "consent_timestamp": utc_now(),
        "privacy_purpose": "To respond to the trial/onboarding request and provide Astraa service information related to the request.",
        "lead_score": 0,
        "status": "New",
        "next_action": "",
    }

    score = score_lead(lead)
    lead["lead_score"] = score
    lead["status"] = lead_status(score)
    lead["next_action"] = next_action(score, tool_interest)

    append_jsonl(LEADS_FILE, lead)

    # Send safe structured event to Arka internal bridge.
    send_astraa_event_to_arka(
        "lead.created",
        {
            "name": lead.get("name"),
            "business_name": lead.get("business_name"),
            "email": lead.get("email"),
            "province": lead.get("province"),
            "industry": lead.get("industry"),
            "business_size": lead.get("business_size"),
            "tool_interest": lead.get("tool_interest"),
            "lead_score": lead.get("lead_score"),
            "status": lead.get("status"),
            "next_action": lead.get("next_action"),
            "source_page": lead.get("source_page"),
            "consent_accepted": lead.get("consent_accepted"),
            "consent_timestamp": lead.get("consent_timestamp"),
        },
        requires_operator_approval=True,
    )

    email_queue_item = build_confirmation_email(lead)
    append_jsonl(EMAIL_QUEUE_FILE, email_queue_item)

    signal = update_sales_signal()

    return jsonify({
        "ok": True,
        "message": "Astraa trial request received.",
        "lead_status": lead["status"],
        "lead_score": lead["lead_score"],
        "next_action": lead["next_action"],
        "sales_channel_signal": signal["sales_channel_signal"],
    }), 201


@astraa_leads.route("/api/leads/report", methods=["GET"])
def leads_report():
    leads = read_jsonl(LEADS_FILE)
    signal = update_sales_signal()

    return jsonify({
        "ok": True,
        "total_leads": len(leads),
        "sales_signal": signal,
    }), 200
