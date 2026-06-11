"""
ARKA Policy Engine — Ardhanarishvara Motherboard
------------------------------------------------
This module provides a unified policy evaluation system used by:
- ARKA Core
- Astra
- Aruhan
- Multi-agent coordination layer

It supports:
- Policy registration
- Policy evaluation
- Policy chaining
- Context-aware rules
- Safe fallback behavior
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Optional
from .registry.policy_registry import PolicyRegistry
from .validators.policy_validator import validate_policy_input


@dataclass
class PolicyResult:
    policy: str
    allowed: bool
    reason: str
    metadata: Optional[Dict[str, Any]] = None


class PolicyEngine:
    """
    Central policy engine for ARKA ecosystem.
    """

    def __init__(self):
        self.registry = PolicyRegistry()

    def evaluate(self, policy_name: str, context: Dict[str, Any]) -> PolicyResult:
        """
        Evaluate a single policy.
        """
        validate_policy_input(policy_name, context)

        policy_fn = self.registry.get(policy_name)
        if not policy_fn:
            return PolicyResult(
                policy=policy_name,
                allowed=True,
                reason="Policy not found — default allow",
                metadata={"missing": True}
            )

        try:
            allowed, reason, metadata = policy_fn(context)
            return PolicyResult(
                policy=policy_name,
                allowed=allowed,
                reason=reason,
                metadata=metadata
            )
        except Exception as e:
            return PolicyResult(
                policy=policy_name,
                allowed=False,
                reason=f"Policy execution error: {e}",
                metadata={"exception": True}
            )

    def evaluate_chain(self, policies: List[str], context: Dict[str, Any]) -> List[PolicyResult]:
        """
        Evaluate multiple policies in sequence.
        """
        results = []
        for p in policies:
            result = self.evaluate(p, context)
            results.append(result)
            if not result.allowed:
                break
        return results
