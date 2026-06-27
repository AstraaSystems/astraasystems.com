"""
capability_readiness_reporter.py

Phase 17A capability readiness reporter for Arka V1.

This module reports capability readiness by combining:
- capability_registry.py
- capability_enablement_contracts.py

It does not:
- execute tools
- run shell commands
- call web/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state
- enable capabilities
- fabricate evidence

Phase 17A is standalone reporting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CapabilityReadiness:
    capability_name: str
    route: str
    registry_enabled: bool
    read_only: bool
    mutates_state: bool
    requires_approval: bool
    enablement_contract: Optional[str]
    contract_exists: bool
    can_enable: bool
    missing_requirement_count: int
    missing_requirements: List[str] = field(default_factory=list)
    status: str = "unknown"
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_name": self.capability_name,
            "route": self.route,
            "registry_enabled": self.registry_enabled,
            "read_only": self.read_only,
            "mutates_state": self.mutates_state,
            "requires_approval": self.requires_approval,
            "enablement_contract": self.enablement_contract,
            "contract_exists": self.contract_exists,
            "can_enable": self.can_enable,
            "missing_requirement_count": self.missing_requirement_count,
            "missing_requirements": list(self.missing_requirements),
            "status": self.status,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


class CapabilityReadinessReporter:
    """
    Reports readiness of registered capabilities.

    Phase 17A does not enable or execute capabilities.
    """

    def list_readiness(
        self,
        available_components: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        capabilities = self._list_capabilities()
        return [
            self._readiness_for_capability(cap, available_components).to_dict()
            for cap in capabilities
        ]

    def get_readiness(
        self,
        capability_name: str,
        available_components: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        for cap in self._list_capabilities():
            if cap.get("name") == capability_name:
                return self._readiness_for_capability(
                    cap,
                    available_components,
                ).to_dict()
        return None

    def summarize(
        self,
        available_components: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        reports = self.list_readiness(available_components)

        summary = {
            "total_capabilities": len(reports),
            "ready": 0,
            "not_ready": 0,
            "approval_required": 0,
            "mutation_future_only": 0,
            "missing_contract": 0,
            "unknown": 0,
            "metadata": self._metadata(),
        }

        for item in reports:
            status = item.get("status", "unknown")
            if status in summary:
                summary[status] += 1
            else:
                summary["unknown"] += 1

        return summary

    def _readiness_for_capability(
        self,
        capability: Dict[str, Any],
        available_components: Optional[List[str]],
    ) -> CapabilityReadiness:
        name = capability.get("name", "")
        route = capability.get("route", "")
        registry_enabled = bool(capability.get("enabled", False))
        read_only = bool(capability.get("read_only", False))
        mutates_state = bool(capability.get("mutates_state", False))
        requires_approval_registry = bool(capability.get("requires_approval", False))

        metadata = capability.get("metadata", {}) or {}
        contract_name = metadata.get("enablement_contract") or name

        decision = self._evaluate_enablement(contract_name, available_components)

        if decision is None:
            return CapabilityReadiness(
                capability_name=name,
                route=route,
                registry_enabled=registry_enabled,
                read_only=read_only,
                mutates_state=mutates_state,
                requires_approval=requires_approval_registry,
                enablement_contract=contract_name,
                contract_exists=False,
                can_enable=False,
                missing_requirement_count=0,
                missing_requirements=[],
                status="missing_contract",
                warnings=["enablement_contract_missing"],
                metadata=self._metadata(),
            )

        missing = list(getattr(decision, "missing_requirements", []) or [])
        contract_requires_approval = bool(getattr(decision, "requires_approval", False))
        allows_mutation = bool(getattr(decision, "allows_mutation", False))
        can_enable = bool(getattr(decision, "can_enable", False))

        warnings = list(getattr(decision, "warnings", []) or [])

        status = self._status(
            registry_enabled=registry_enabled,
            can_enable=can_enable,
            missing=missing,
            requires_approval=contract_requires_approval or requires_approval_registry,
            allows_mutation=allows_mutation or mutates_state,
        )

        return CapabilityReadiness(
            capability_name=name,
            route=route,
            registry_enabled=registry_enabled,
            read_only=read_only,
            mutates_state=mutates_state,
            requires_approval=contract_requires_approval or requires_approval_registry,
            enablement_contract=contract_name,
            contract_exists=True,
            can_enable=can_enable,
            missing_requirement_count=len(missing),
            missing_requirements=missing,
            status=status,
            warnings=warnings,
            metadata=self._metadata(),
        )

    def _status(
        self,
        registry_enabled: bool,
        can_enable: bool,
        missing: List[str],
        requires_approval: bool,
        allows_mutation: bool,
    ) -> str:
        if allows_mutation:
            return "mutation_future_only"

        if requires_approval:
            return "approval_required"

        if registry_enabled and can_enable and not missing:
            return "ready"

        if missing:
            return "not_ready"

        if not registry_enabled:
            return "not_ready"

        return "unknown"

    def _list_capabilities(self) -> List[Dict[str, Any]]:
        try:
            try:
                from arka_v1.core.capability_registry import list_capabilities
            except Exception:
                from core.capability_registry import list_capabilities

            return list_capabilities()
        except Exception:
            return []

    def _evaluate_enablement(
        self,
        capability_name: str,
        available_components: Optional[List[str]],
    ) -> Optional[Any]:
        try:
            try:
                from arka_v1.core.capability_enablement_contracts import evaluate_enablement
            except Exception:
                from core.capability_enablement_contracts import evaluate_enablement

            return evaluate_enablement(
                capability_name,
                available_components or [],
            )
        except Exception:
            return None

    def _metadata(self) -> Dict[str, Any]:
        return {
            "reporter_version": "phase17",
            "reporter": "arka_v1.core.capability_readiness_reporter",
            "external_calls": False,
            "memory_mutation": False,
            "tool_execution": False,
            "runtime_writes": False,
            "capability_enablement": False,
            "fabricated_results": False,
        }


def list_capability_readiness(
    available_components: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    return CapabilityReadinessReporter().list_readiness(available_components)


def get_capability_readiness(
    capability_name: str,
    available_components: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    return CapabilityReadinessReporter().get_readiness(
        capability_name,
        available_components,
    )


def summarize_capability_readiness(
    available_components: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return CapabilityReadinessReporter().summarize(available_components)
