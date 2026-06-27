"""
capability_registry.py

Phase 11A capability registry for Arka V1.

This module defines safe capability metadata and route-to-capability decisions.

It does not:
- execute tools
- run shell commands
- call web/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state
- approve destructive actions
- fabricate evidence

Phase 11A is registry/decision only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Capability:
    name: str
    route: str
    source_type: Optional[str]
    enabled: bool
    read_only: bool
    mutates_state: bool
    requires_approval: bool
    executor_name: Optional[str]
    evidence_types: List[str] = field(default_factory=list)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "route": self.route,
            "source_type": self.source_type,
            "enabled": self.enabled,
            "read_only": self.read_only,
            "mutates_state": self.mutates_state,
            "requires_approval": self.requires_approval,
            "executor_name": self.executor_name,
            "evidence_types": list(self.evidence_types),
            "description": self.description,
            "metadata": dict(self.metadata),
        }


@dataclass
class CapabilityDecision:
    matched: bool
    route: str
    capability_name: Optional[str] = None
    enabled: bool = False
    read_only: bool = False
    mutates_state: bool = False
    requires_approval: bool = False
    executor_name: Optional[str] = None
    evidence_types: List[str] = field(default_factory=list)
    reason: str = ""
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matched": self.matched,
            "route": self.route,
            "capability_name": self.capability_name,
            "enabled": self.enabled,
            "read_only": self.read_only,
            "mutates_state": self.mutates_state,
            "requires_approval": self.requires_approval,
            "executor_name": self.executor_name,
            "evidence_types": list(self.evidence_types),
            "reason": self.reason,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


class CapabilityRegistry:
    """
    Registry of known Arka capabilities.

    Phase 11A only declares and selects capabilities.
    It does not execute them.
    """

    def __init__(self) -> None:
        self._capabilities = self._default_capabilities()

    def list_capabilities(self) -> List[Dict[str, Any]]:
        return [cap.to_dict() for cap in self._capabilities]

    def get_capability(self, name: str) -> Optional[Dict[str, Any]]:
        for cap in self._capabilities:
            if cap.name == name:
                return cap.to_dict()
        return None

    def find_for_route(self, route: str) -> CapabilityDecision:
        route = str(route or "").strip()

        for cap in self._capabilities:
            if cap.route == route:
                return self._decision_from_capability(cap)

        return CapabilityDecision(
            matched=False,
            route=route,
            reason="No registered capability matched this route.",
            warnings=["capability_not_registered"],
            metadata=self._metadata(),
        )

    def decide_for_context(self, context: Dict[str, Any]) -> CapabilityDecision:
        source_route = context.get("source_route", {}) or {}
        route = str(source_route.get("route", "") or "")
        return self.find_for_route(route)

    def _decision_from_capability(self, cap: Capability) -> CapabilityDecision:
        warnings: List[str] = []

        if not cap.enabled:
            warnings.append("capability_registered_but_disabled")

        if cap.mutates_state:
            warnings.append("capability_mutates_state")

        if cap.requires_approval:
            warnings.append("capability_requires_approval")

        if not cap.read_only:
            warnings.append("capability_not_read_only")

        if cap.enabled and cap.read_only and not cap.mutates_state and not cap.requires_approval:
            reason = "Route matched enabled read-only capability."
        elif not cap.enabled:
            reason = "Route matched a registered capability, but it is not enabled."
        elif cap.requires_approval:
            reason = "Route matched a capability that requires approval."
        else:
            reason = "Route matched a capability with safety restrictions."

        return CapabilityDecision(
            matched=True,
            route=cap.route,
            capability_name=cap.name,
            enabled=cap.enabled,
            read_only=cap.read_only,
            mutates_state=cap.mutates_state,
            requires_approval=cap.requires_approval,
            executor_name=cap.executor_name,
            evidence_types=list(cap.evidence_types),
            reason=reason,
            warnings=warnings,
            metadata=self._metadata(),
        )

    def _metadata(self) -> Dict[str, Any]:
        return {
            "registry_version": "phase11",
            "registry": "arka_v1.core.capability_registry",
            "external_calls": False,
            "memory_mutation": False,
            "tool_execution": False,
            "runtime_writes": False,
            "destructive_actions_allowed": False,
        }

    def _default_capabilities(self) -> List[Capability]:
        return [
            Capability(
                name="profile_context",
                route="LOCAL_PROFILE",
                source_type="profile",
                enabled=True,
                read_only=True,
                mutates_state=False,
                requires_approval=False,
                executor_name=None,
                evidence_types=[],
                description="Trusted local profile/family context already loaded by profile_loader.",
                metadata={"phase": "phase11", "enablement_contract": "profile_context", "ARKA_CAPABILITY_ENABLEMENT_REGISTRY_LINK_PHASE15C": True},
            ),
            Capability(
                name="local_git_readonly",
                route="GITHUB_REQUIRED",
                source_type="github_or_git",
                enabled=True,
                read_only=True,
                mutates_state=False,
                requires_approval=False,
                executor_name="source_execution_bridge.local_git_readonly",
                evidence_types=[
                    "git_status_branch",
                    "git_status_short",
                    "git_branch_current",
                    "git_log_recent",
                    "git_remote_verbose",
                ],
                description="Safe read-only local Git evidence collection.",
                metadata={"phase": "phase11", "enablement_contract": "local_git_readonly", "ARKA_CAPABILITY_ENABLEMENT_REGISTRY_LINK_PHASE15C": True},
            ),
            Capability(
                name="math_executor_placeholder",
                route="MATH_REQUIRED",
                source_type="math",
                enabled=False,
                read_only=True,
                mutates_state=False,
                requires_approval=False,
                executor_name="math_executor_placeholder",
                evidence_types=[],
                description="Placeholder for future safe Math OS execution.",
                metadata={"phase": "phase11", "placeholder": True, "enablement_contract": "math_executor_placeholder", "ARKA_CAPABILITY_ENABLEMENT_REGISTRY_LINK_PHASE15C": True},
            ),
            Capability(
                name="astraa_status_placeholder",
                route="ASTRAA_STATUS_REQUIRED",
                source_type="astraa_status",
                enabled=False,
                read_only=True,
                mutates_state=False,
                requires_approval=False,
                executor_name="astraa_status_connector_placeholder",
                evidence_types=[],
                description="Placeholder for future read-only Astraa status connector.",
                metadata={"phase": "phase11", "placeholder": True, "enablement_contract": "astraa_status_placeholder", "ARKA_CAPABILITY_ENABLEMENT_REGISTRY_LINK_PHASE15C": True},
            ),
            Capability(
                name="server_health_placeholder",
                route="SERVER_REQUIRED",
                source_type="server_status",
                enabled=False,
                read_only=True,
                mutates_state=False,
                requires_approval=False,
                executor_name="server_health_connector_placeholder",
                evidence_types=[],
                description="Placeholder for future read-only server/API health connector.",
                metadata={"phase": "phase11", "placeholder": True, "enablement_contract": "server_health_placeholder", "ARKA_CAPABILITY_ENABLEMENT_REGISTRY_LINK_PHASE15C": True},
            ),
            Capability(
                name="web_source_placeholder",
                route="WEB_SOURCE_REQUIRED",
                source_type="web",
                enabled=False,
                read_only=True,
                mutates_state=False,
                requires_approval=False,
                executor_name="web_source_connector_placeholder",
                evidence_types=[],
                description="Placeholder for future web/source connector.",
                metadata={"phase": "phase11", "placeholder": True, "enablement_contract": "web_source_placeholder", "ARKA_CAPABILITY_ENABLEMENT_REGISTRY_LINK_PHASE15C": True},
            ),
            Capability(
                name="payment_status_placeholder",
                route="PAYMENT_REQUIRED",
                source_type="payment_status",
                enabled=False,
                read_only=True,
                mutates_state=False,
                requires_approval=False,
                executor_name="payment_status_connector_placeholder",
                evidence_types=[],
                description="Placeholder for future read-only payment status connector.",
                metadata={"phase": "phase11", "placeholder": True},
            ),
            Capability(
                name="action_verification_placeholder",
                route="ACTION_VERIFICATION_REQUIRED",
                source_type="action_verification",
                enabled=False,
                read_only=True,
                mutates_state=False,
                requires_approval=True,
                executor_name="action_verification_placeholder",
                evidence_types=[],
                description="Placeholder for future action verification; approval required.",
                metadata={"phase": "phase11", "placeholder": True},
            ),
        ]


def list_capabilities() -> List[Dict[str, Any]]:
    return CapabilityRegistry().list_capabilities()


def get_capability(name: str) -> Optional[Dict[str, Any]]:
    return CapabilityRegistry().get_capability(name)


def find_capability_for_route(route: str) -> CapabilityDecision:
    return CapabilityRegistry().find_for_route(route)


def decide_capability_for_context(context: Dict[str, Any]) -> CapabilityDecision:
    return CapabilityRegistry().decide_for_context(context)
