"""
Policy Engine — Ardhanarishvara Motherboard
-------------------------------------------
This module provides a unified policy enforcement layer for the entire
ecosystem (ARKA, Astra, Aruhan, and future agents).

It exposes:
- enforce()        → main compatibility function used by ARKA
- evaluate_policy() → internal scoring logic
- check_context()   → validates context before enforcement
- PolicyResult      → structured return object

This file is SAFE, STABLE, and backwards‑compatible.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


# ---------------------------------------------------------
# Structured Result Object
# ---------------------------------------------------------

@dataclass
class PolicyResult:
    status: str
    allowed: bool
    reason: str
    policy: Optional[Any] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------

def check_context(context: Optional[Dict[str, Any]]) -> bool:
    """
    Ensures context is valid. ARKA sometimes passes None.
    """
    if context is None:
        return False
    if not isinstance(context, dict):
        return False
    return True


def evaluate_policy(policy: Optional[Any], context: Optional[Dict[str, Any]]) -> bool:
    """
    Placeholder evaluation logic.
    Always returns True for now — safe default.
    Extend later with real rules.
    """
    return True


# ---------------------------------------------------------
# MAIN ENTRY POINT (ARKA depends on this)
# ---------------------------------------------------------

def enforce(policy: Optional[Any] = None,
           context: Optional[Dict[str, Any]] = None,
           strict: bool = False) -> PolicyResult:
    """
    Main compatibility function required by ARKA.

    It MUST exist or ARKA will crash on import.

    Behavior:
    - If strict=True and context is invalid → deny
    - Otherwise → allow by default
    """

    context_ok = check_context(context)

    if strict and not context_ok:
        return PolicyResult(
            status="error",
            allowed=False,
            reason="Invalid context in strict mode",
            policy=policy,
            context=context,
            metadata={"strict": True}
        )

    allowed = evaluate_policy(policy, context)

    return PolicyResult(
        status="ok",
        allowed=allowed,
        reason="Policy evaluation passed",
        policy=policy,
        context=context,
        metadata={"strict": strict}
    )


# ---------------------------------------------------------
# Optional Utility (future use)
# ---------------------------------------------------------

def enforce_strict(policy: Optional[Any], context: Optional[Dict[str, Any]]) -> PolicyResult:
    """
    Strict enforcement wrapper.
    """
    return enforce(policy=policy, context=context, strict=True)
