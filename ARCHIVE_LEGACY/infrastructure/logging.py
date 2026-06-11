"""
Unified Logging System — Ardhanarishvara Motherboard
----------------------------------------------------
This module provides a safe, minimal, backwards‑compatible logging
interface for ARKA, Astra, Aruhan, and future agents.

ARKA depends on:
- log(message, level)

This file guarantees that function exists and behaves safely.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


# ---------------------------------------------------------
# Structured Log Entry
# ---------------------------------------------------------

@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------

def _timestamp() -> str:
    """
    Generate ISO‑8601 timestamp.
    """
    return datetime.utcnow().isoformat() + "Z"


def _normalize_level(level: Optional[str]) -> str:
    """
    Normalize log level.
    """
    if level is None:
        return "info"
    return str(level).lower()


# ---------------------------------------------------------
# MAIN ENTRY POINT (ARKA depends on this)
# ---------------------------------------------------------

def log(message: Any,
        level: Optional[str] = "info",
        context: Optional[Dict[str, Any]] = None,
        emit: bool = False) -> LogEntry:
    """
    Main compatibility function required by ARKA.

    Behavior:
    - Always returns a structured LogEntry
    - Never raises exceptions
    - If emit=True → prints to stdout (optional)
    """

    level_norm = _normalize_level(level)

    entry = LogEntry(
        timestamp=_timestamp(),
        level=level_norm,
        message=str(message),
        metadata={"context": context}
    )

    if emit:
        print(f"[{entry.timestamp}] [{entry.level.upper()}] {entry.message}")

    return entry


# ---------------------------------------------------------
# Utility: convenience wrappers
# ---------------------------------------------------------

def log_info(message: Any, context: Optional[Dict[str, Any]] = None) -> LogEntry:
    return log(message, level="info", context=context)


def log_warning(message: Any, context: Optional[Dict[str, Any]] = None) -> LogEntry:
    return log(message, level="warning", context=context)


def log_error(message: Any, context: Optional[Dict[str, Any]] = None) -> LogEntry:
    return log(message, level="error", context=context)
