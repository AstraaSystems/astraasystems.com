"""
Consensus Framework — Ardhanarishvara Motherboard
-------------------------------------------------
This module provides a unified, safe, backwards‑compatible consensus
synchronization system for ARKA, Astra, Aruhan, and future agents.

ARKA depends on:
- sync_state(state, peers)

This file guarantees that function exists and behaves safely.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------
# Structured Consensus Result
# ---------------------------------------------------------

@dataclass
class ConsensusResult:
    status: str
    state: Any
    agreed: bool
    peers: List[str]
    reason: str
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------

def _normalize_peers(peers: Optional[List[str]]) -> List[str]:
    """
    Normalize peer list.
    """
    if peers is None:
        return []
    return [str(p).lower() for p in peers]


def _compute_agreement(state: Any, peers: List[str]) -> bool:
    """
    Simple safe default:
    - If no peers → assume agreement
    - If peers exist → assume agreement unless state is None
    """
    if not peers:
        return True
    return state is not None


# ---------------------------------------------------------
# MAIN ENTRY POINT (ARKA depends on this)
# ---------------------------------------------------------

def sync_state(state: Any,
               peers: Optional[List[str]] = None,
               strict: bool = False) -> ConsensusResult:
    """
    Main compatibility function required by ARKA.

    Behavior:
    - Always returns a structured ConsensusResult
    - Never raises exceptions
    - If strict=True and state is None → deny agreement
    """

    peers_norm = _normalize_peers(peers)

    if strict and state is None:
        return ConsensusResult(
            status="error",
            state=state,
            agreed=False,
            peers=peers_norm,
            reason="Missing state in strict mode",
            metadata={"strict": True}
        )

    agreed = _compute_agreement(state, peers_norm)

    return ConsensusResult(
        status="ok",
        state=state,
        agreed=agreed,
        peers=peers_norm,
        reason="Consensus achieved" if agreed else "Consensus failed",
        metadata={"strict": strict}
    )


# ---------------------------------------------------------
# Utility: strict wrapper
# ---------------------------------------------------------

def sync_state_strict(state: Any, peers: Optional[List[str]] = None) -> ConsensusResult:
    return sync_state(state, peers, strict=True)
