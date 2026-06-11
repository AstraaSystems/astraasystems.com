"""
Security Policies — Ardhanarishvara Motherboard
------------------------------------------------
This module provides a unified, safe, backwards‑compatible access control
system for ARKA, Astra, Aruhan, and future agents.

ARKA depends on:
- check_access(user, action)

This file guarantees that function exists and behaves safely.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


# ---------------------------------------------------------
# Structured Access Result
# ---------------------------------------------------------

@dataclass
class AccessResult:
    status: str
    allowed: bool
    user: Optional[str]
    action: Optional[str]
    reason: str
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Default Access Rules (safe fallback)
# ---------------------------------------------------------

DEFAULT_RULES = {
    "system": ["*"],          # system can do anything
    "admin": ["*"],           # admin can do anything
    "arka": ["read", "write", "execute"],
    "astra": ["read", "write"],
    "aruhan": ["read"],
    "guest": ["read"]
}


# ---------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------

def _normalize(user: Optional[str]) -> str:
    """
    Normalize user identity.
    """
    if user is None:
        return "guest"
    return str(user).lower()


def _is_allowed(user: str, action: str, rules: Dict[str, Any]) -> bool:
    """
    Check if user is allowed to perform action.
    """
    if user not in rules:
        return False

    allowed_actions = rules[user]

    if "*" in allowed_actions:
        return True

    return action in allowed_actions


# ---------------------------------------------------------
# MAIN ENTRY POINT (ARKA depends on this)
# ---------------------------------------------------------

def check_access(user: Optional[str],
                 action: Optional[str],
                 rules: Optional[Dict[str, Any]] = None,
                 strict: bool = False) -> AccessResult:
    """
    Main compatibility function required by ARKA.

    Behavior:
    - If strict=True and user/action invalid → deny
    - Otherwise → allow safe defaults
    """

    if rules is None:
        rules = DEFAULT_RULES

    user_norm = _normalize(user)

    if action is None:
        if strict:
            return AccessResult(
                status="error",
                allowed=False,
                user=user_norm,
                action=action,
                reason="Missing action in strict mode",
                metadata={"strict": True}
            )
        action = "read"

    allowed = _is_allowed(user_norm, action, rules)

    return AccessResult(
        status="ok",
        allowed=allowed,
        user=user_norm,
        action=action,
        reason="Access granted" if allowed else "Access denied",
        metadata={"strict": strict, "ruleset": "default"}
    )


# ---------------------------------------------------------
# Utility: strict wrapper
# ---------------------------------------------------------

def check_access_strict(user: Optional[str], action: Optional[str]) -> AccessResult:
    return check_access(user, action, strict=True)
