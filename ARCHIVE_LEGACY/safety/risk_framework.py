"""
Risk Framework — Ardhanarishvara Motherboard
--------------------------------------------
This module provides a unified, safe, backwards‑compatible risk assessment
system for ARKA, Astra, Aruhan, and future agents.

ARKA depends on:
- assess(event, context)

This file guarantees that function exists and behaves safely.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


# ---------------------------------------------------------
# Structured Risk Result
# ---------------------------------------------------------

@dataclass
class RiskResult:
    status: str
    level: str
    score: float
    event: Optional[str]
    context: Optional[Dict[str, Any]]
    reason: str
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Default Risk Weights (safe fallback)
# ---------------------------------------------------------

DEFAULT_WEIGHTS = {
    "error": 0.9,
    "exception": 0.8,
    "timeout": 0.7,
    "anomaly": 0.6,
    "warning": 0.4,
    "info": 0.1
}


# ---------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------

def _normalize_event(event: Optional[str]) -> str:
    """
    Normalize event name.
    """
    if event is None:
        return "unknown"
    return str(event).lower()


def _compute_score(event: str, context: Optional[Dict[str, Any]]) -> float:
    """
    Compute a simple risk score based on event type.
    """
    weight = DEFAULT_WEIGHTS.get(event, 0.2)

    # Context can increase risk slightly
    context_factor = 1.0
    if context and isinstance(context, dict):
        context_factor += min(len(context) * 0.05, 0.5)

    return round(weight * context_factor, 3)


def _score_to_level(score: float) -> str:
    """
    Convert numeric score to human‑readable risk level.
    """
    if score >= 0.8:
        return "critical"
    if score >= 0.6:
        return "high"
    if score >= 0.4:
        return "medium"
    if score >= 0.2:
        return "low"
    return "minimal"


# ---------------------------------------------------------
# MAIN ENTRY POINT (ARKA depends on this)
# ---------------------------------------------------------

def assess(event: Optional[str],
           context: Optional[Dict[str, Any]] = None,
           strict: bool = False) -> RiskResult:
    """
    Main compatibility function required by ARKA.

    Behavior:
    - Always returns a structured RiskResult
    - Never raises exceptions
    - If strict=True and event is missing → treat as high risk
    """

    event_norm = _normalize_event(event)

    if strict and event is None:
        score = 0.8
        level = "high"
        return RiskResult(
            status="error",
            level=level,
            score=score,
            event=event_norm,
            context=context,
            reason="Missing event in strict mode",
            metadata={"strict": True}
        )

    score = _compute_score(event_norm, context)
    level = _score_to_level(score)

    return RiskResult(
        status="ok",
        level=level,
        score=score,
        event=event_norm,
        context=context,
        reason="Risk assessment completed",
        metadata={"strict": strict}
    )


# ---------------------------------------------------------
# Utility: strict wrapper
# ---------------------------------------------------------

def assess_strict(event: Optional[str], context: Optional[Dict[str, Any]] = None) -> RiskResult:
    return assess(event, context, strict=True)
