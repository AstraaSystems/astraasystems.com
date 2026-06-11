"""
Default Global Policies for ARKA
--------------------------------
These policies apply across all agents.
"""

from typing import Dict, Any, Tuple


def arka_global_policy(context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    goal = context.get("goal", "")

    if not goal:
        return False, "Missing goal in context", {}

    if "destroy" in goal.lower() or "harm" in goal.lower():
        return False, "Goal violates safety constraints", {"blocked": True}

    return True, "Goal allowed", {}
