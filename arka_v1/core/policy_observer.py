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

    # ARKA_CAPABILITY_OBSERVER_PHASE13A
    # Safe capability metadata only. No raw prompt, raw response, or source content.
    capability_name: Optional[str] = None
    capability_enabled: Optional[bool] = None
    capability_read_only: Optional[bool] = None
    capability_requires_approval: Optional[bool] = None
    capability_mutates_state: Optional[bool] = None
    capability_blocked_reason: Optional[str] = None

    # ARKA_ENABLEMENT_OBSERVER_PHASE16A
    # Safe enablement contract metadata only.
    enablement_contract: Optional[str] = None
    enablement_can_enable: Optional[bool] = None
    enablement_missing_requirement_count: Optional[int] = None
    enablement_requires_approval: Optional[bool] = None
    enablement_allows_mutation: Optional[bool] = None
    enablement_read_only_required: Optional[bool] = None

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
            "capability_name": self.capability_name,
            "capability_enabled": self.capability_enabled,
            "capability_read_only": self.capability_read_only,
            "capability_requires_approval": self.capability_requires_approval,
            "capability_mutates_state": self.capability_mutates_state,
            "capability_blocked_reason": self.capability_blocked_reason,
            "enablement_contract": self.enablement_contract,
            "enablement_can_enable": self.enablement_can_enable,
            "enablement_missing_requirement_count": self.enablement_missing_requirement_count,
            "enablement_requires_approval": self.enablement_requires_approval,
            "enablement_allows_mutation": self.enablement_allows_mutation,
            "enablement_read_only_required": self.enablement_read_only_required,
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

        capability_info = self._capability_info(
            context=context,
            source_execution=source_execution,
        )

        enablement_info = self._enablement_info(capability_info)

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
            capability_name=capability_info.get("capability_name"),
            capability_enabled=capability_info.get("capability_enabled"),
            capability_read_only=capability_info.get("capability_read_only"),
            capability_requires_approval=capability_info.get("capability_requires_approval"),
            capability_mutates_state=capability_info.get("capability_mutates_state"),
            capability_blocked_reason=capability_info.get("capability_blocked_reason"),
            enablement_contract=enablement_info.get("enablement_contract"),
            enablement_can_enable=enablement_info.get("enablement_can_enable"),
            enablement_missing_requirement_count=enablement_info.get("enablement_missing_requirement_count"),
            enablement_requires_approval=enablement_info.get("enablement_requires_approval"),
            enablement_allows_mutation=enablement_info.get("enablement_allows_mutation"),
            enablement_read_only_required=enablement_info.get("enablement_read_only_required"),
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

    def _capability_info(
        self,
        context: Dict[str, Any],
        source_execution: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Return safe capability metadata.

        This intentionally excludes raw prompt, raw response, and source content.
        """

        capability_decision = self._capability_decision_from_source_execution(
            source_execution
        )

        if capability_decision is None:
            capability_decision = self._capability_decision_from_registry(context)

        return {
            "capability_name": self._safe_str(
                capability_decision.get("capability_name")
                if capability_decision
                else None
            ),
            "capability_enabled": self._safe_bool_or_none(
                capability_decision.get("enabled")
                if capability_decision
                else None
            ),
            "capability_read_only": self._safe_bool_or_none(
                capability_decision.get("read_only")
                if capability_decision
                else None
            ),
            "capability_requires_approval": self._safe_bool_or_none(
                capability_decision.get("requires_approval")
                if capability_decision
                else None
            ),
            "capability_mutates_state": self._safe_bool_or_none(
                capability_decision.get("mutates_state")
                if capability_decision
                else None
            ),
            "capability_blocked_reason": self._safe_str(
                source_execution.get("blocked_reason")
            ),
        }

    def _capability_decision_from_source_execution(
        self,
        source_execution: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Extract capability decision from source execution metadata when present.
        """

        metadata = source_execution.get("metadata", {}) or {}
        decision = metadata.get("capability_decision")

        if isinstance(decision, dict):
            return decision

        return None

    def _capability_decision_from_registry(
        self,
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Safely ask capability_registry for route metadata when available.

        This does not execute tools. It only reads registry metadata.
        """

        try:
            try:
                from arka_v1.core.capability_registry import decide_capability_for_context
            except Exception:
                from core.capability_registry import decide_capability_for_context

            decision = decide_capability_for_context(context)

            if hasattr(decision, "to_dict"):
                return decision.to_dict()

            if isinstance(decision, dict):
                return decision

        except Exception:
            return None

        return None

    def _enablement_info(
        self,
        capability_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Return safe enablement contract metadata.

        This does not execute tools or connectors. It only evaluates contract metadata.
        """

        capability_name = capability_info.get("capability_name")

        if not capability_name:
            return {
                "enablement_contract": None,
                "enablement_can_enable": None,
                "enablement_missing_requirement_count": None,
                "enablement_requires_approval": None,
                "enablement_allows_mutation": None,
                "enablement_read_only_required": None,
            }

        try:
            try:
                from arka_v1.core.capability_enablement_contracts import (
                    evaluate_enablement,
                )
            except Exception:
                from core.capability_enablement_contracts import (
                    evaluate_enablement,
                )

            decision = evaluate_enablement(capability_name, [])

            return {
                "enablement_contract": capability_name,
                "enablement_can_enable": bool(getattr(decision, "can_enable", False)),
                "enablement_missing_requirement_count": len(
                    getattr(decision, "missing_requirements", []) or []
                ),
                "enablement_requires_approval": bool(
                    getattr(decision, "requires_approval", False)
                ),
                "enablement_allows_mutation": bool(
                    getattr(decision, "allows_mutation", False)
                ),
                "enablement_read_only_required": bool(
                    getattr(decision, "read_only_required", True)
                ),
            }

        except Exception:
            return {
                "enablement_contract": capability_name,
                "enablement_can_enable": None,
                "enablement_missing_requirement_count": None,
                "enablement_requires_approval": None,
                "enablement_allows_mutation": None,
                "enablement_read_only_required": None,
            }

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
