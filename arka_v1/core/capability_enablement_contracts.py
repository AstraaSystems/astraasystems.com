"""
capability_enablement_contracts.py

Phase 15A capability enablement contracts for Arka V1.

This module defines what must be true before disabled placeholder
capabilities can be safely enabled.

It does not:
- execute tools
- run shell commands
- call web/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state
- approve destructive actions
- fabricate evidence

Phase 15A is standalone contract metadata only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class CapabilityEnablementContract:
    capability_name: str
    route: str
    can_enable_by_default: bool
    required_components: List[str] = field(default_factory=list)
    required_evidence_schema: List[str] = field(default_factory=list)
    required_safety_rules: List[str] = field(default_factory=list)
    requires_approval: bool = False
    allows_mutation: bool = False
    read_only_required: bool = True
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_name": self.capability_name,
            "route": self.route,
            "can_enable_by_default": self.can_enable_by_default,
            "required_components": list(self.required_components),
            "required_evidence_schema": list(self.required_evidence_schema),
            "required_safety_rules": list(self.required_safety_rules),
            "requires_approval": self.requires_approval,
            "allows_mutation": self.allows_mutation,
            "read_only_required": self.read_only_required,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }


@dataclass
class CapabilityEnablementDecision:
    capability_name: str
    route: str
    can_enable: bool
    missing_requirements: List[str] = field(default_factory=list)
    requires_approval: bool = False
    allows_mutation: bool = False
    read_only_required: bool = True
    reason: str = ""
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_name": self.capability_name,
            "route": self.route,
            "can_enable": self.can_enable,
            "missing_requirements": list(self.missing_requirements),
            "requires_approval": self.requires_approval,
            "allows_mutation": self.allows_mutation,
            "read_only_required": self.read_only_required,
            "reason": self.reason,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


class CapabilityEnablementContracts:
    """
    Registry of enablement contracts.

    Phase 15A defines requirements only. It does not enable or execute anything.
    """

    def __init__(self) -> None:
        self._contracts = self._default_contracts()

    def list_contracts(self) -> List[Dict[str, Any]]:
        return [contract.to_dict() for contract in self._contracts]

    def get_contract(self, capability_name: str) -> Optional[Dict[str, Any]]:
        for contract in self._contracts:
            if contract.capability_name == capability_name:
                return contract.to_dict()
        return None

    def get_contract_by_route(self, route: str) -> Optional[Dict[str, Any]]:
        for contract in self._contracts:
            if contract.route == route:
                return contract.to_dict()
        return None

    def evaluate_enablement(
        self,
        capability_name: str,
        available_components: Optional[List[str]] = None,
    ) -> CapabilityEnablementDecision:
        available = set(available_components or [])
        contract = self._find_contract(capability_name)

        if contract is None:
            return CapabilityEnablementDecision(
                capability_name=capability_name,
                route="",
                can_enable=False,
                missing_requirements=[],
                reason="No enablement contract exists for this capability.",
                warnings=["enablement_contract_not_registered"],
                metadata=self._metadata(),
            )

        return self._evaluate_contract(contract, available)

    def evaluate_route_enablement(
        self,
        route: str,
        available_components: Optional[List[str]] = None,
    ) -> CapabilityEnablementDecision:
        available = set(available_components or [])
        contract = self._find_contract_by_route(route)

        if contract is None:
            return CapabilityEnablementDecision(
                capability_name="",
                route=route,
                can_enable=False,
                missing_requirements=[],
                reason="No enablement contract exists for this route.",
                warnings=["enablement_contract_not_registered"],
                metadata=self._metadata(),
            )

        return self._evaluate_contract(contract, available)

    def _find_contract(self, capability_name: str) -> Optional[CapabilityEnablementContract]:
        for contract in self._contracts:
            if contract.capability_name == capability_name:
                return contract
        return None

    def _find_contract_by_route(self, route: str) -> Optional[CapabilityEnablementContract]:
        for contract in self._contracts:
            if contract.route == route:
                return contract
        return None

    def _evaluate_contract(
        self,
        contract: CapabilityEnablementContract,
        available_components: set,
    ) -> CapabilityEnablementDecision:
        required = set(contract.required_components)
        missing = sorted(required - available_components)

        warnings: List[str] = []

        if missing:
            warnings.append("missing_required_components")

        if contract.requires_approval:
            warnings.append("approval_required")

        if contract.allows_mutation:
            warnings.append("mutation_capable_contract")

        if not contract.read_only_required:
            warnings.append("read_only_not_required")

        can_enable = (
            contract.can_enable_by_default
            and not missing
            and not contract.allows_mutation
        )

        if can_enable:
            reason = "All required components are present and contract permits enablement."
        elif missing:
            reason = "Capability cannot be enabled because required components are missing."
        elif contract.allows_mutation:
            reason = "Capability cannot be enabled by Phase 15A because mutation-capable contracts need a future approval layer."
        elif not contract.can_enable_by_default:
            reason = "Capability is contract-defined but not enabled by default."
        else:
            reason = "Capability cannot be enabled under current contract rules."

        return CapabilityEnablementDecision(
            capability_name=contract.capability_name,
            route=contract.route,
            can_enable=can_enable,
            missing_requirements=missing,
            requires_approval=contract.requires_approval,
            allows_mutation=contract.allows_mutation,
            read_only_required=contract.read_only_required,
            reason=reason,
            warnings=warnings,
            metadata=self._metadata(),
        )

    def _metadata(self) -> Dict[str, Any]:
        return {
            "contracts_version": "phase15",
            "contracts": "arka_v1.core.capability_enablement_contracts",
            "external_calls": False,
            "memory_mutation": False,
            "tool_execution": False,
            "runtime_writes": False,
            "destructive_actions_allowed": False,
            "fabricated_results": False,
        }

    def _default_contracts(self) -> List[CapabilityEnablementContract]:
        return [
            CapabilityEnablementContract(
                capability_name="local_git_readonly",
                route="GITHUB_REQUIRED",
                can_enable_by_default=True,
                required_components=[
                    "safe_git_readonly_executor",
                    "unsafe_git_action_guard",
                    "git_evidence_schema",
                ],
                required_evidence_schema=[
                    "source",
                    "type",
                    "content",
                    "metadata.command",
                ],
                required_safety_rules=[
                    "read_only_git_commands_only",
                    "block_push_commit_reset_merge_deploy",
                    "no_arbitrary_shell_expansion",
                ],
                requires_approval=False,
                allows_mutation=False,
                read_only_required=True,
                notes="Already enabled capability. Contract documents required safety components.",
                metadata={"phase": "phase15", "already_enabled": True},
            ),
            CapabilityEnablementContract(
                capability_name="web_source_placeholder",
                route="WEB_SOURCE_REQUIRED",
                can_enable_by_default=False,
                required_components=[
                    "approved_web_source_connector",
                    "source_result_schema",
                    "citation_or_source_url_normalizer",
                    "timeout_and_failure_policy",
                    "no_secret_leak_guard",
                ],
                required_evidence_schema=[
                    "source",
                    "title",
                    "url",
                    "retrieved_at",
                    "snippet_or_summary",
                ],
                required_safety_rules=[
                    "do_not_claim_web_results_without_verified_sources",
                    "redact_secrets",
                    "handle_timeouts_as_limitations",
                ],
                requires_approval=False,
                allows_mutation=False,
                read_only_required=True,
                notes="Live web answers require verified source results before enablement.",
                metadata={"phase": "phase15", "placeholder": True},
            ),
            CapabilityEnablementContract(
                capability_name="astraa_status_placeholder",
                route="ASTRAA_STATUS_REQUIRED",
                can_enable_by_default=False,
                required_components=[
                    "approved_astraa_status_connector",
                    "status_result_schema",
                    "site_or_app_target_config",
                    "timeout_and_failure_policy",
                    "no_fake_status_claim_guard",
                ],
                required_evidence_schema=[
                    "target",
                    "status",
                    "checked_at",
                    "evidence_source",
                ],
                required_safety_rules=[
                    "read_only_status_checks_only",
                    "do_not_claim_up_down_without_verified_evidence",
                    "redact_sensitive_urls_or_tokens",
                ],
                requires_approval=False,
                allows_mutation=False,
                read_only_required=True,
                notes="Astraa status reporting requires a verified read-only status connector.",
                metadata={"phase": "phase15", "placeholder": True},
            ),
            CapabilityEnablementContract(
                capability_name="server_health_placeholder",
                route="SERVER_REQUIRED",
                can_enable_by_default=False,
                required_components=[
                    "approved_server_health_connector",
                    "health_result_schema",
                    "allowed_targets_config",
                    "timeout_and_failure_policy",
                    "no_destructive_probe_guard",
                ],
                required_evidence_schema=[
                    "target",
                    "health_status",
                    "checked_at",
                    "evidence_source",
                ],
                required_safety_rules=[
                    "read_only_health_checks_only",
                    "no_arbitrary_shell",
                    "no_destructive_probes",
                ],
                requires_approval=False,
                allows_mutation=False,
                read_only_required=True,
                notes="Server health checks must be read-only and target-restricted.",
                metadata={"phase": "phase15", "placeholder": True},
            ),
            CapabilityEnablementContract(
                capability_name="payment_status_placeholder",
                route="PAYMENT_REQUIRED",
                can_enable_by_default=False,
                required_components=[
                    "approved_payment_status_connector",
                    "payment_status_result_schema",
                    "read_only_payment_scope",
                    "secret_redaction_guard",
                    "no_payment_mutation_guard",
                ],
                required_evidence_schema=[
                    "provider",
                    "status",
                    "checked_at",
                    "reference_id_redacted",
                ],
                required_safety_rules=[
                    "read_only_payment_status_only",
                    "no_payment_mutations",
                    "redact_payment_identifiers",
                    "redact_secrets",
                ],
                requires_approval=True,
                allows_mutation=False,
                read_only_required=True,
                notes="Payment status is sensitive; keep approval-required until a safe read-only contract is reviewed.",
                metadata={"phase": "phase15", "placeholder": True, "sensitive": True},
            ),
            CapabilityEnablementContract(
                capability_name="math_executor_placeholder",
                route="MATH_REQUIRED",
                can_enable_by_default=False,
                required_components=[
                    "approved_math_executor",
                    "calculation_input_schema",
                    "calculation_output_schema",
                    "numeric_trace_or_explanation",
                    "no_state_mutation_guard",
                ],
                required_evidence_schema=[
                    "inputs",
                    "method",
                    "result",
                    "trace_or_explanation",
                ],
                required_safety_rules=[
                    "deterministic_calculation_path",
                    "no_state_mutation",
                    "explain_assumptions",
                ],
                requires_approval=False,
                allows_mutation=False,
                read_only_required=True,
                notes="Future safe Math OS bridge can satisfy this contract.",
                metadata={"phase": "phase15", "placeholder": True},
            ),
            CapabilityEnablementContract(
                capability_name="action_verification_placeholder",
                route="ACTION_VERIFICATION_REQUIRED",
                can_enable_by_default=False,
                required_components=[
                    "approval_layer",
                    "verified_execution_log_schema",
                    "action_scope_contract",
                    "rollback_or_safety_policy",
                    "operator_confirmation_policy",
                ],
                required_evidence_schema=[
                    "action",
                    "approved_by",
                    "executed_at",
                    "result",
                    "verification_id",
                ],
                required_safety_rules=[
                    "approval_required_before_mutation",
                    "verified_execution_required_before_claim",
                    "no_unapproved_destructive_actions",
                ],
                requires_approval=True,
                allows_mutation=True,
                read_only_required=False,
                notes="Future mutation workflows belong here, not in source execution.",
                metadata={"phase": "phase15", "placeholder": True, "mutation_future_only": True},
            ),
        ]


def list_enablement_contracts() -> List[Dict[str, Any]]:
    return CapabilityEnablementContracts().list_contracts()


def get_enablement_contract(capability_name: str) -> Optional[Dict[str, Any]]:
    return CapabilityEnablementContracts().get_contract(capability_name)


def get_enablement_contract_by_route(route: str) -> Optional[Dict[str, Any]]:
    return CapabilityEnablementContracts().get_contract_by_route(route)


def evaluate_enablement(
    capability_name: str,
    available_components: Optional[List[str]] = None,
) -> CapabilityEnablementDecision:
    return CapabilityEnablementContracts().evaluate_enablement(
        capability_name=capability_name,
        available_components=available_components,
    )


def evaluate_route_enablement(
    route: str,
    available_components: Optional[List[str]] = None,
) -> CapabilityEnablementDecision:
    return CapabilityEnablementContracts().evaluate_route_enablement(
        route=route,
        available_components=available_components,
    )
