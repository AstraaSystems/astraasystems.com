"""
Unified Error Handling — Ardhanarishvara Motherboard
----------------------------------------------------
This module provides a safe, minimal, backwards‑compatible error handling
system for ARKA, Astra, Aruhan, and future agents.

ARKA depends on:
- handle(error)

This file guarantees that function exists and behaves safely.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


# ---------------------------------------------------------
# Structured Error Result
# ---------------------------------------------------------

@dataclass
class ErrorResult:
    status: str
    handled: bool
    error_type: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------

def _extract_error_info(error: Exception) -> Dict[str, str]:
    """
    Safely extract error type and message.
    """
    return {
        "type": error.__class__.__name__,
        "message": str(error)
    }


# ---------------------------------------------------------
# MAIN ENTRY POINT (ARKA depends on this)
# ---------------------------------------------------------

def handle(error: Exception,
           context: Optional[Dict[str, Any]] = None,
           escalate: bool = False) -> ErrorResult:
    """
    Main compatibility function required by ARKA.

    Behavior:
    - Always returns a structured ErrorResult
    - Never raises exceptions
    - If escalate=True → mark as unhandled but still safe
    """

    info = _extract_error_info(error)

    if escalate:
        return ErrorResult(
            status="error",
            handled=False,
            error_type=info["type"],
            message=info["message"],
            metadata={"escalated": True, "context": context}
        )

    # Default safe handling
    return ErrorResult(
        status="ok",
        handled=True,
        error_type=info["type"],
        message=info["message"],
        metadata={"escalated": False, "context": context}
    )


# ---------------------------------------------------------
# Optional Utility
# ---------------------------------------------------------

def handle_safely(func, *args, **kwargs) -> ErrorResult:
    """
    Wrap any function call and convert exceptions into ErrorResult.
    """
    try:
        func(*args, **kwargs)
        return ErrorResult(
            status="ok",
            handled=True,
            error_type="None",
            message="No error",
            metadata={"wrapped": True}
        )
    except Exception as e:
        return handle(e)
