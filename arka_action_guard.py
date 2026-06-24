"""
Arka HQ Action Guard v1

Purpose:
- Central approval gate for any future Arka action.
- Read/report is allowed.
- External actions are blocked unless explicitly approved by operator policy.

This guard protects:
- payments
- customer unlocks
- email sending
- trading
- file deletion
- production API calls
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PENDING_ACTIONS_FILE = DATA_DIR / "arka_pending_actions.jsonl"


READ_ONLY_ACTIONS = {
    "read_status",
    "read_leads",
    "read_sales_signal",
    "read_bridge_events",
    "read_email_queue",
    "summarize",
    "explain",
}


BLOCKED_BY_DEFAULT = {
    "send_email",
    "unlock_customer",
    "activate_subscription",
    "run_payment",
    "verify_payment",
    "moneris_preload",
    "moneris_receipt",
    "place_trade",
    "submit_order",
    "connect_broker",
    "delete_file",
    "modify_vault",
    "external_api_write",
}


@dataclass
class GuardResult:
    allowed: bool
    mode: str
    reason: str
    requires_operator_approval: bool


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def check_action(action_type: str, payload: dict[str, Any] | None = None) -> GuardResult:
    action = (action_type or "").strip().lower()
    payload = payload or {}

    if action in READ_ONLY_ACTIONS:
        return GuardResult(
            allowed=True,
            mode="read_only",
            reason="Read-only action allowed.",
            requires_operator_approval=False,
        )

    if action in BLOCKED_BY_DEFAULT:
        append_jsonl(PENDING_ACTIONS_FILE, {
            "created_at": now_utc(),
            "action_type": action,
            "payload": payload,
            "status": "pending_operator_approval",
            "reason": "Blocked by Arka HQ Action Guard v1.",
        })

        return GuardResult(
            allowed=False,
            mode="blocked_pending_approval",
            reason="Action blocked and queued for operator approval.",
            requires_operator_approval=True,
        )

    append_jsonl(PENDING_ACTIONS_FILE, {
        "created_at": now_utc(),
        "action_type": action,
        "payload": payload,
        "status": "unknown_action_review_required",
        "reason": "Unknown action type. Manual review required.",
    })

    return GuardResult(
        allowed=False,
        mode="unknown_action_review_required",
        reason="Unknown action type. Manual review required.",
        requires_operator_approval=True,
    )


def guard_status() -> dict[str, Any]:
    return {
        "guard": "Arka HQ Action Guard v1",
        "default_mode": "read_only",
        "read_only_actions": sorted(READ_ONLY_ACTIONS),
        "blocked_by_default": sorted(BLOCKED_BY_DEFAULT),
        "pending_actions_file": str(PENDING_ACTIONS_FILE),
    }


if __name__ == "__main__":
    print(json.dumps(guard_status(), indent=2))
