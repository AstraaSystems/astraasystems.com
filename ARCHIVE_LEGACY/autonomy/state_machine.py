"""
Unified State Machine — Ardhanarishvara Motherboard
---------------------------------------------------
This module provides a safe, minimal, backwards‑compatible state machine
for ARKA, Astra, Aruhan, and future agents.

ARKA depends on:
- transition(current_state, event)

This file guarantees that function exists and behaves safely.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


# ---------------------------------------------------------
# State Transition Result
# ---------------------------------------------------------

@dataclass
class TransitionResult:
    previous: str
    event: str
    next: str
    allowed: bool
    reason: str
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Default State Map (safe fallback)
# ---------------------------------------------------------

DEFAULT_TRANSITIONS = {
    "idle": {
        "start": "running",
        "error": "error"
    },
    "running": {
        "pause": "paused",
        "stop": "idle",
        "error": "error"
    },
    "paused": {
        "resume": "running",
        "stop": "idle",
        "error": "error"
    },
    "error": {
        "reset": "idle"
    }
}


# ---------------------------------------------------------
# MAIN ENTRY POINT (ARKA depends on this)
# ---------------------------------------------------------

def transition(current_state: str,
               event: str,
               transitions: Optional[Dict[str, Dict[str, str]]] = None
               ) -> TransitionResult:
    """
    Main compatibility function required by ARKA.

    Ensures ARKA can import and run without crashing.

    Behavior:
    - If transition is valid → move to next state
    - If invalid → remain in current state but return allowed=False
    """

    if transitions is None:
        transitions = DEFAULT_TRANSITIONS

    state_map = transitions.get(current_state, {})

    if event in state_map:
        next_state = state_map[event]
        return TransitionResult(
            previous=current_state,
            event=event,
            next=next_state,
            allowed=True,
            reason="Transition allowed",
            metadata={"default_map": transitions is DEFAULT_TRANSITIONS}
        )

    # Invalid transition
    return TransitionResult(
        previous=current_state,
        event=event,
        next=current_state,
        allowed=False,
        reason="Invalid transition",
        metadata={"default_map": transitions is DEFAULT_TRANSITIONS}
    )


# ---------------------------------------------------------
# Utility: check if transition is allowed
# ---------------------------------------------------------

def can_transition(current_state: str,
                   event: str,
                   transitions: Optional[Dict[str, Dict[str, str]]] = None
                   ) -> bool:
    if transitions is None:
        transitions = DEFAULT_TRANSITIONS
    return event in transitions.get(current_state, {})
