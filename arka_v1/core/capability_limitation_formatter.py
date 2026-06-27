"""
capability_limitation_formatter.py

Phase 14A capability-aware limitation formatter for Arka V1.

This module converts internal capability limitation states into clear,
user-facing limitation messages.

It does not:
- execute tools
- enable disabled capabilities
- call web/search/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state
- log raw prompts
- fabricate external results
- claim web/Astraa/server/payment checks happened

Phase 14A is standalone formatting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class CapabilityLimitationResult:
    formatted: bool
    response: str
    reason: str = ""
    route: Optional[str] = None
    capability_name: Optional[str] = None
    blocked_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "formatted": self.formatted,
            "response": self.response,
            "reason": self.reason,
            "route": self.route,
            "capability_name": self.capability_name,
            "blocked_reason": self.blocked_reason,
            "metadata": dict(self.metadata),
        }


class CapabilityLimitationFormatter:
    """
    Formats capability-disabled/blocked states into user-facing messages.

    This formatter only uses safe metadata already present in context.
    """

    def format(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> CapabilityLimitationResult:
        context = context or {}

        source_route = context.get("source_route", {}) or {}
        source_execution = context.get("source_execution", {}) or {}
        execution_metadata = source_execution.get("metadata", {}) or {}

        route = self._safe_str(source_route.get("route"))
        source_type = self._safe_str(source_route.get("source_type"))
        blocked_reason = self._safe_str(source_execution.get("blocked_reason"))

        capability_name = self._safe_str(execution_metadata.get("capability_name"))

        capability_decision = execution_metadata.get("capability_decision")
        if capability_name is None and isinstance(capability_decision, dict):
            capability_name = self._safe_str(capability_decision.get("capability_name"))

        if blocked_reason is None:
            return CapabilityLimitationResult(
                formatted=False,
                response=response,
                reason="No capability blocked_reason was available.",
                route=route,
                capability_name=capability_name,
                blocked_reason=blocked_reason,
                metadata=self._metadata(source_type=source_type),
            )

        # Disabled placeholders.
        if blocked_reason == "capability_disabled":
            return self._format_capability_disabled(
                response=response,
                route=route,
                source_type=source_type,
                capability_name=capability_name,
                blocked_reason=blocked_reason,
            )

        # Unsafe Git/action prompt blocked by read-only Git executor.
        if blocked_reason == "unsafe_git_action_blocked":
            return self._finish(
                text=(
                    "I can inspect Git safely, but I won’t run or claim a Git action "
                    "such as push, commit, reset, merge, or deploy from this read-only path. "
                    "No Git action was performed."
                ),
                reason="Formatted unsafe Git action limitation.",
                route=route,
                source_type=source_type,
                capability_name=capability_name,
                blocked_reason=blocked_reason,
            )

        # Approval-controlled capability.
        if blocked_reason == "capability_requires_approval":
            return self._finish(
                text=(
                    "This request needs an approval-controlled execution path. "
                    "I won’t perform or confirm that action without verified approval "
                    "and execution evidence."
                ),
                reason="Formatted approval-required capability limitation.",
                route=route,
                source_type=source_type,
                capability_name=capability_name,
                blocked_reason=blocked_reason,
            )

        # Mutating capability.
        if blocked_reason == "capability_mutates_state":
            return self._finish(
                text=(
                    "This request maps to a capability that could change system state. "
                    "I won’t perform or confirm that action from this safe read-only path."
                ),
                reason="Formatted mutating capability limitation.",
                route=route,
                source_type=source_type,
                capability_name=capability_name,
                blocked_reason=blocked_reason,
            )

        # Non-read-only capability.
        if blocked_reason == "capability_not_read_only":
            return self._finish(
                text=(
                    "This request maps to a capability that is not marked read-only. "
                    "I won’t execute it from this path without a stricter approval layer."
                ),
                reason="Formatted non-read-only capability limitation.",
                route=route,
                source_type=source_type,
                capability_name=capability_name,
                blocked_reason=blocked_reason,
            )

        # Not registered.
        if blocked_reason == "capability_not_registered":
            return self._finish(
                text=(
                    "I don’t have a registered capability for this request yet. "
                    "I won’t guess or claim results without a defined capability and verified evidence."
                ),
                reason="Formatted unregistered capability limitation.",
                route=route,
                source_type=source_type,
                capability_name=capability_name,
                blocked_reason=blocked_reason,
            )

        return CapabilityLimitationResult(
            formatted=False,
            response=response,
            reason=f"No Phase 14A limitation rule matched blocked_reason: {blocked_reason}",
            route=route,
            capability_name=capability_name,
            blocked_reason=blocked_reason,
            metadata=self._metadata(source_type=source_type),
        )

    def _format_capability_disabled(
        self,
        response: str,
        route: Optional[str],
        source_type: Optional[str],
        capability_name: Optional[str],
        blocked_reason: Optional[str],
    ) -> CapabilityLimitationResult:
        if route == "WEB_SOURCE_REQUIRED" or capability_name == "web_source_placeholder":
            text = (
                "I can’t perform a live web lookup from this local Arka path yet. "
                "The web source capability is registered, but it is currently disabled. "
                "I won’t make up a web-sourced answer without verified results."
            )
            reason = "Formatted disabled web source capability limitation."

        elif route == "ASTRAA_STATUS_REQUIRED" or capability_name == "astraa_status_placeholder":
            text = (
                "I can’t verify Astraa website/app status from this local Arka path yet. "
                "The Astraa status capability is registered, but it is currently disabled. "
                "I won’t claim the site or app status without verified evidence."
            )
            reason = "Formatted disabled Astraa status capability limitation."

        elif route == "SERVER_REQUIRED" or capability_name == "server_health_placeholder":
            text = (
                "I can’t check backend/server health from this local Arka path yet. "
                "The server health capability is registered, but it is currently disabled. "
                "I won’t claim server status without verified evidence."
            )
            reason = "Formatted disabled server health capability limitation."

        elif route == "PAYMENT_REQUIRED" or capability_name == "payment_status_placeholder":
            text = (
                "I can’t check payment or Moneris status from this local Arka path yet. "
                "The payment status capability is registered, but it is currently disabled. "
                "I won’t claim payment status without verified evidence."
            )
            reason = "Formatted disabled payment status capability limitation."

        else:
            text = (
                "This capability is registered, but it is currently disabled. "
                "I won’t claim results without verified evidence from an enabled capability."
            )
            reason = "Formatted generic disabled capability limitation."

        return self._finish(
            text=text,
            reason=reason,
            route=route,
            source_type=source_type,
            capability_name=capability_name,
            blocked_reason=blocked_reason,
        )

    def _finish(
        self,
        text: str,
        reason: str,
        route: Optional[str],
        source_type: Optional[str],
        capability_name: Optional[str],
        blocked_reason: Optional[str],
    ) -> CapabilityLimitationResult:
        return CapabilityLimitationResult(
            formatted=True,
            response=text,
            reason=reason,
            route=route,
            capability_name=capability_name,
            blocked_reason=blocked_reason,
            metadata=self._metadata(source_type=source_type),
        )

    def _safe_str(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _metadata(self, source_type: Optional[str]) -> Dict[str, Any]:
        return {
            "formatter_version": "phase14",
            "formatter": "arka_v1.core.capability_limitation_formatter",
            "source_type": source_type,
            "external_calls": False,
            "memory_mutation": False,
            "tool_execution": False,
            "runtime_writes": False,
            "raw_prompt_logged": False,
            "raw_response_logged": False,
            "source_content_logged": False,
            "profile_values_logged": False,
            "fabricated_results": False,
        }


def format_capability_limitation(
    prompt: str,
    response: str,
    context: Optional[Dict[str, Any]] = None,
) -> CapabilityLimitationResult:
    """
    Convenience function for Phase 14 capability-aware limitation formatting.
    """

    formatter = CapabilityLimitationFormatter()
    return formatter.format(prompt=prompt, response=response, context=context)
