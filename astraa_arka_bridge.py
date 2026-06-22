"""
Astraa ↔ Arka Internal Bridge

Purpose:
- Let Astraa send structured business events to Arka.
- Let Arka write recommendations back to Astraa.
- Keep public website/Workspace separated from internal intelligence.
- Require operator approval before production actions.

Does NOT:
- expose Arka publicly
- let website visitors call Arka directly
- unlock customer accounts
- run payments
- send emails automatically
- perform trading
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
BRIDGE_EVENTS_FILE = DATA_DIR / "astraa_arka_bridge.jsonl"
ARKA_RECOMMENDATIONS_FILE = DATA_DIR / "arka_recommendations.jsonl"


def utc_now() -> str:
    """Return current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_data_dir() -> None:
    """Ensure local data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    """Append a dictionary as one JSONL record."""
    ensure_data_dir()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read JSONL records from a file, skipping malformed lines."""
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def send_astraa_event_to_arka(
    event_type: str,
    payload: dict[str, Any],
    *,
    source: str = "astraa",
    requires_operator_approval: bool = True,
) -> dict[str, Any]:
    """
    Send a safe structured Astraa event to the internal Arka bridge.

    This writes to a local JSONL queue. It does not expose Arka publicly and
    does not perform any production action by itself.
    """
    event = {
        "event_id": f"astraa_evt_{uuid.uuid4().hex}",
        "created_at": utc_now(),
        "source": source,
        "target": "arka",
        "event_type": event_type,
        "requires_operator_approval": requires_operator_approval,
        "payload": payload,
    }

    append_jsonl(BRIDGE_EVENTS_FILE, event)
    return event


def write_arka_recommendation(
    related_event_id: str,
    recommendation: str,
    *,
    priority: str = "normal",
    risk_level: str = "controlled",
    requires_operator_approval: bool = True,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Write an Arka recommendation back to Astraa.

    Recommendations are advisory by default and require operator approval.
    """
    item = {
        "recommendation_id": f"arka_rec_{uuid.uuid4().hex}",
        "created_at": utc_now(),
        "source": "arka",
        "target": "astraa",
        "related_event_id": related_event_id,
        "recommendation": recommendation,
        "priority": priority,
        "risk_level": risk_level,
        "requires_operator_approval": requires_operator_approval,
        "metadata": metadata or {},
    }

    append_jsonl(ARKA_RECOMMENDATIONS_FILE, item)
    return item


def get_bridge_summary() -> dict[str, Any]:
    """Return a lightweight summary of bridge activity."""
    events = read_jsonl(BRIDGE_EVENTS_FILE)
    recommendations = read_jsonl(ARKA_RECOMMENDATIONS_FILE)

    return {
        "events_to_arka": len(events),
        "recommendations_from_arka": len(recommendations),
        "latest_event": events[-1] if events else None,
        "latest_recommendation": recommendations[-1] if recommendations else None,
    }
