"""
policy_observer.py

Phase 10A policy observability module for Arka V1.

This module creates safe, compact diagnostic observations about response policy
decisions.

It does not:
- execute tools
- call web/search/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state by default
- log raw prompts by default
- log raw responses by default
- log family/profile values
- log source content
- log secrets/tokens

Phase 10A is standalone observability only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PolicyObservation:
    """
    Safe compact observation of a response policy decision.

    This intentionally excludes:
    - raw prompt
    - raw response
    - profile/family values
    - source result content
    - secrets/tokens
    """

    observed: bool
    event_type: str = "response_policy_observation"
    route: Optional[str] = None
    source_type: Optional[str] = None
    style: Optional[str] = None
    evidence_available: bool = False
    allow_evidence_formatting: bool = False
    show_sources: bool = False
    show_limitations: bool = False
    action_blocked: bool = False
    limitation_selected: bool = False
    formatter_used: bool = False
    source_execution_status: Optional[str] = None
    source_execution_executed: Optional[bool] = None
    validation_status: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a safe dictionary representation.
        """

        return {
            "observed": self.observed,
            "event_type": self.event_type,
            "route": self.route,
            "source_type": self.source_type,
            "style": self.style,
            "evidence_available": self.evidence_available,
            "allow_evidence_formatting": self.allow_evidence_formatting,
            "show_sources": self.show_sources,
            "show_limitations": self.show_limitations,
            "action_blocked": self.action_blocked,
            "limitation_selected": self.limitation_selected,
            "formatter_used": self.formatter_used,
            "source_execution_status": self.source_execution_status,
            "source_execution_executed": self.source_execution_executed,
            "validation_status": self.validation_status,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


class PolicyObserver:
    """
    Builds safe response-policy observation events.

    Phase 10A does not write logs by default.
    """

    ACTION_BLOCKED_STYLES = {
        "ACTION_BLOCKED",
    }

    LIMITATION_STYLES = {
        "LIMITATION_ONLY",
    }

    def observe(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        policy_decision: Optional[Any] = None,
        formatter_result: Optional[Any] = None,
        validation_result: Optional[Any] = None,
        enabled: bool = False,
    ) -> PolicyObservation:
        """
        Build a safe observation event.

        enabled=False still returns the observation object but performs no writes.
        """

        context = context or {}

        source_route = context.get("source_route", {}) or {}
        source_execution = context.get("source_execution", {}) or {}

        route = self._safe_str(source_route.get("route"))
        source_type = self._safe_str(source_route.get("source_type"))

        sources = context.get("sources", []) or []
        source_results = context.get("source_results", []) or []
        verified_actions = context.get("verified_actions", []) or []

        evidence_available = bool(sources or source_results or verified_actions)

        style = self._style_from_policy(policy_decision)

        allow_evidence_formatting = bool(
            getattr(policy_decision, "allow_evidence_formatting", False)
            if policy_decision is not None
            else False
        )

        show_sources = bool(
            getattr(policy_decision, "show_sources", False)
            if policy_decision is not None
            else False
        )

        show_limitations = bool(
            getattr(policy_decision, "show_limitations", False)
            if policy_decision is not None
            else False
        )

        policy_warnings = list(
            getattr(policy_decision, "policy_warnings", [])
            if policy_decision is not None
            else []
        )

        formatter_used = bool(
            getattr(formatter_result, "formatted", False)
            if formatter_result is not None
            else False
        )

        validation_status = self._validation_status(validation_result)

        action_blocked = style in self.ACTION_BLOCKED_STYLES
        limitation_selected = style in self.LIMITATION_STYLES

        warnings = []
        warnings.extend(policy_warnings)

        if not enabled:
            warnings.append("observer_not_persisting_enabled_false")

        observation = PolicyObservation(
            observed=True,
            route=route,
            source_type=source_type,
            style=style,
            evidence_available=evidence_available,
            allow_evidence_formatting=allow_evidence_formatting,
            show_sources=show_sources,
            show_limitations=show_limitations,
            action_blocked=action_blocked,
            limitation_selected=limitation_selected,
            formatter_used=formatter_used,
            source_execution_status=self._safe_str(source_execution.get("status")),
            source_execution_executed=self._safe_bool_or_none(
                source_execution.get("executed")
            ),
            validation_status=validation_status,
            warnings=warnings,
            metadata=self._metadata(enabled=enabled),
        )

        return observation

    def _style_from_policy(self, policy_decision: Optional[Any]) -> Optional[str]:
        if policy_decision is None:
            return None

        style = getattr(policy_decision, "style", None)

        if style is None:
            return None

        return str(getattr(style, "value", style))

    def _validation_status(self, validation_result: Optional[Any]) -> Optional[str]:
        if validation_result is None:
            return None

        status = getattr(validation_result, "status", None)

        if status is None:
            return None

        return str(getattr(status, "value", status))

    def _safe_str(self, value: Any) -> Optional[str]:
        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return None

        return text

    def _safe_bool_or_none(self, value: Any) -> Optional[bool]:
        if value is None:
            return None

        return bool(value)

    def _metadata(self, enabled: bool) -> Dict[str, Any]:
        return {
            "observer_version": "phase10",
            "observer": "arka_v1.core.policy_observer",
            "enabled": bool(enabled),
            "persisted": False,
            "external_calls": False,
            "memory_mutation": False,
            "tool_execution": False,
            "raw_prompt_logged": False,
            "raw_response_logged": False,
            "source_content_logged": False,
            "profile_values_logged": False,
            "sensitive_fields_omitted": True,
        }


def observe_response_policy(
    prompt: str,
    response: str,
    context: Optional[Dict[str, Any]] = None,
    policy_decision: Optional[Any] = None,
    formatter_result: Optional[Any] = None,
    validation_result: Optional[Any] = None,
    enabled: bool = False,
) -> PolicyObservation:
    """
    Convenience function for Phase 10 policy observability.
    """

    observer = PolicyObserver()

    return observer.observe(
        prompt=prompt,
        response=response,
        context=context,
        policy_decision=policy_decision,
        formatter_result=formatter_result,
        validation_result=validation_result,
        enabled=enabled,
    )
