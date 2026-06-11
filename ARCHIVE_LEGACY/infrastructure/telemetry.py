"""
Telemetry System — Ardhanarishvara Motherboard
----------------------------------------------
This module provides a unified, safe, backwards‑compatible telemetry
recording system for ARKA, Astra, Aruhan, and future agents.

ARKA depends on:
- record(event, data)

This file guarantees that function exists and behaves safely.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


# ---------------------------------------------------------
# Structured Telemetry Event
# ---------------------------------------------------------

@dataclass
class TelemetryEvent:
    timestamp: str
    event: str
    data: Dict[str, Any]
    status: str
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------

def _timestamp() -> str:
    """
    Generate ISO‑8601 timestamp.
    """
    return datetime.utcnow().isoformat() + "Z"


def _normalize_event(event: Optional[str]) -> str:
    """
    Normalize event name.
    """
    if event is None:
        return "unknown"
    return str(event).lower()


def _normalize_data(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Ensure data is always a dictionary.
    """
    if data is None:
        return {}
    if not isinstance(data, dict):
        return {"value": data}
    return data


# ---------------------------------------------------------
# MAIN ENTRY POINT (ARKA depends on this)
# ---------------------------------------------------------

def record(event: Optional[str],
           data: Optional[Dict[str, Any]] = None,
           emit: bool = False,
           strict: bool = False) -> TelemetryEvent:
    """
    Main compatibility function required by ARKA.

    Behavior:
    - Always returns a structured TelemetryEvent
    - Never raises exceptions
    - If strict=True and event is missing → mark as error
    - If emit=True → prints to stdout (optional)
    """

    event_norm = _normalize_event(event)
    data_norm = _normalize_data(data)

    if strict and event is None:
        entry = TelemetryEvent(
            timestamp=_timestamp(),
            event=event_norm,
            data=data_norm,
            status="error",
            metadata={"strict": True}
        )
        if emit:
            print(f"[{entry.timestamp}] [TELEMETRY-ERROR] {entry.event} {entry.data}")
        return entry

    entry = TelemetryEvent(
        timestamp=_timestamp(),
        event=event_norm,
        data=data_norm,
        status="ok",
        metadata={"strict": strict}
    )

    if emit:
        print(f"[{entry.timestamp}] [TELEMETRY] {entry.event} {entry.data}")

    return entry


# ---------------------------------------------------------
# Utility: strict wrapper
# ---------------------------------------------------------

def record_strict(event: Optional[str],
                  data: Optional[Dict[str, Any]] = None) -> TelemetryEvent:
    return record(event, data, strict=True)
