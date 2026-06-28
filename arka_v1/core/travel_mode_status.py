"""
travel_mode_status.py

Phase 19A Travel / Delivery Mode operational status module for Arka V1.

This module builds a safe founder-facing operational dashboard for short
travel/delivery check-ins.

It may summarize:
- current stable checkpoint supplied by caller
- proof branch supplied by caller
- bundle path supplied by caller
- source-of-truth machine supplied by caller
- safe operating rules
- Phase 18 readiness summary

It does not:
- execute shell commands
- inspect Git directly
- mutate Git
- call connectors
- enable capabilities
- mutate memory
- write runtime state
- expose secrets
- fabricate live server/web/payment status

Phase 19A is standalone reporting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


DEFAULT_TRAVEL_WARNINGS = [
    "Use DESKTOP-K930S6S main PC as the Arka HQ source of truth.",
    "Use the travel laptop as a remote terminal or emergency fallback only.",
    "Do not copy secrets, payment data, runtime state, or private memory to the travel laptop.",
    "Do not push from the travel clone unless push access is intentionally re-enabled.",
    "Do not enable disabled capabilities until their enablement contracts are satisfied.",
    "Do not claim live web, server, payment, or Astraa status without verified evidence.",
]


DEFAULT_SAFE_OPERATING_RULES = [
    "Real Arka HQ work should happen through the remote main PC WSL repo.",
    "The travel laptop clone should remain fallback/read-only unless there is an emergency.",
    "Before any development step, confirm git status is clean and the latest checkpoint is expected.",
    "After each completed phase, create or verify the proof branch, tags, and bundle.",
    "Keep capability work read-only, evidence-backed, and contract-aware.",
]


@dataclass
class TravelModeStatus:
    mode: str
    source_of_truth: str
    remote_context: str
    current_commit: str
    current_tag: str
    proof_branch: str
    bundle_path: str
    readiness_summary: str
    ready_count: int
    not_ready_count: int
    approval_required_count: int
    mutation_future_only_count: int
    missing_contract_count: int
    unknown_count: int
    safe_operating_rules: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    next_safe_action: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "source_of_truth": self.source_of_truth,
            "remote_context": self.remote_context,
            "current_commit": self.current_commit,
            "current_tag": self.current_tag,
            "proof_branch": self.proof_branch,
            "bundle_path": self.bundle_path,
            "readiness_summary": self.readiness_summary,
            "ready_count": self.ready_count,
            "not_ready_count": self.not_ready_count,
            "approval_required_count": self.approval_required_count,
            "mutation_future_only_count": self.mutation_future_only_count,
            "missing_contract_count": self.missing_contract_count,
            "unknown_count": self.unknown_count,
            "safe_operating_rules": list(self.safe_operating_rules),
            "warnings": list(self.warnings),
            "next_safe_action": self.next_safe_action,
            "metadata": dict(self.metadata),
        }


class TravelModeStatusBuilder:
    """
    Builds a safe travel/delivery mode status object.

    This class does not execute commands or inspect the environment directly.
    It only formats supplied checkpoint values and safe readiness summaries.
    """

    def build(
        self,
        current_commit: str,
        current_tag: str,
        proof_branch: str,
        bundle_path: str,
        source_of_truth: str = "DESKTOP-K930S6S",
        remote_context: str = "travel_laptop_to_main_pc_remote",
        mode: str = "Travel / Delivery Mode",
        available_components: Optional[List[str]] = None,
        extra_warnings: Optional[List[str]] = None,
    ) -> TravelModeStatus:
        readiness_result = self._readiness_summary(
            available_components=available_components,
        )
        readiness_counts = self._readiness_counts(
            available_components=available_components,
        )

        warnings = list(DEFAULT_TRAVEL_WARNINGS)
        for warning in extra_warnings or []:
            if warning and warning not in warnings:
                warnings.append(str(warning))

        next_safe_action = (
            "Continue only from the main PC remote WSL repo after confirming a clean working tree."
        )

        return TravelModeStatus(
            mode=mode,
            source_of_truth=self._safe_str(source_of_truth) or "DESKTOP-K930S6S",
            remote_context=self._safe_str(remote_context) or "travel_laptop_to_main_pc_remote",
            current_commit=self._safe_str(current_commit) or "unknown_commit",
            current_tag=self._safe_str(current_tag) or "unknown_tag",
            proof_branch=self._safe_str(proof_branch) or "unknown_proof_branch",
            bundle_path=self._safe_str(bundle_path) or "unknown_bundle_path",
            readiness_summary=readiness_result,
            ready_count=readiness_counts.get("ready", 0),
            not_ready_count=readiness_counts.get("not_ready", 0),
            approval_required_count=readiness_counts.get("approval_required", 0),
            mutation_future_only_count=readiness_counts.get("mutation_future_only", 0),
            missing_contract_count=readiness_counts.get("missing_contract", 0),
            unknown_count=readiness_counts.get("unknown", 0),
            safe_operating_rules=list(DEFAULT_SAFE_OPERATING_RULES),
            warnings=warnings,
            next_safe_action=next_safe_action,
            metadata=self._metadata(),
        )

    def format_text(self, status: TravelModeStatus) -> str:
        lines = [
            "Arka Travel / Delivery Mode Status",
            "",
            f"Mode: {status.mode}",
            f"Source of truth: {status.source_of_truth}",
            f"Remote context: {status.remote_context}",
            f"Current checkpoint: {status.current_commit}",
            f"Stable tag: {status.current_tag}",
            f"Proof branch: {status.proof_branch}",
            f"Bundle: {status.bundle_path}",
            "",
            "Capability readiness:",
            f"- Ready: {status.ready_count}",
            f"- Not ready: {status.not_ready_count}",
            f"- Approval required: {status.approval_required_count}",
            f"- Future mutation only: {status.mutation_future_only_count}",
            f"- Missing contract: {status.missing_contract_count}",
            f"- Unknown: {status.unknown_count}",
            "",
            "Readiness summary:",
            status.readiness_summary,
            "",
            "Safe operating rules:",
        ]

        for rule in status.safe_operating_rules:
            lines.append(f"- {rule}")

        lines.append("")
        lines.append("Warnings:")

        for warning in status.warnings:
            lines.append(f"- {warning}")

        lines.extend([
            "",
            f"Next safe action: {status.next_safe_action}",
            "",
            "No tools, connectors, capabilities, runtime state, or secrets were executed or modified by this status report.",
        ])

        return "\n".join(lines)

    def _readiness_summary(
        self,
        available_components: Optional[List[str]],
    ) -> str:
        try:
            try:
                from arka_v1.core.readiness_summary_formatter import (
                    format_all_readiness_summaries,
                )
            except Exception:
                from core.readiness_summary_formatter import (
                    format_all_readiness_summaries,
                )

            result = format_all_readiness_summaries(
                available_components=available_components,
                include_missing_requirements=True,
            )

            return getattr(
                result,
                "summary",
                "No readiness summary was available.",
            )
        except Exception:
            return "No readiness summary was available."

    def _readiness_counts(
        self,
        available_components: Optional[List[str]],
    ) -> Dict[str, int]:
        try:
            try:
                from arka_v1.core.capability_readiness_reporter import (
                    summarize_capability_readiness,
                )
            except Exception:
                from core.capability_readiness_reporter import (
                    summarize_capability_readiness,
                )

            summary = summarize_capability_readiness(
                available_components=available_components,
            )

            return {
                "ready": int(summary.get("ready", 0) or 0),
                "not_ready": int(summary.get("not_ready", 0) or 0),
                "approval_required": int(summary.get("approval_required", 0) or 0),
                "mutation_future_only": int(summary.get("mutation_future_only", 0) or 0),
                "missing_contract": int(summary.get("missing_contract", 0) or 0),
                "unknown": int(summary.get("unknown", 0) or 0),
            }
        except Exception:
            return {
                "ready": 0,
                "not_ready": 0,
                "approval_required": 0,
                "mutation_future_only": 0,
                "missing_contract": 0,
                "unknown": 0,
            }

    def _safe_str(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _metadata(self) -> Dict[str, Any]:
        return {
            "status_version": "phase19",
            "module": "arka_v1.core.travel_mode_status",
            "external_calls": False,
            "shell_execution": False,
            "git_mutation": False,
            "memory_mutation": False,
            "runtime_writes": False,
            "tool_execution": False,
            "connector_execution": False,
            "capability_enablement": False,
            "secret_exposure": False,
            "fabricated_results": False,
        }


def build_travel_mode_status(
    current_commit: str,
    current_tag: str,
    proof_branch: str,
    bundle_path: str,
    source_of_truth: str = "DESKTOP-K930S6S",
    remote_context: str = "travel_laptop_to_main_pc_remote",
    mode: str = "Travel / Delivery Mode",
    available_components: Optional[List[str]] = None,
    extra_warnings: Optional[List[str]] = None,
) -> TravelModeStatus:
    return TravelModeStatusBuilder().build(
        current_commit=current_commit,
        current_tag=current_tag,
        proof_branch=proof_branch,
        bundle_path=bundle_path,
        source_of_truth=source_of_truth,
        remote_context=remote_context,
        mode=mode,
        available_components=available_components,
        extra_warnings=extra_warnings,
    )


def format_travel_mode_status_text(status: TravelModeStatus) -> str:
    return TravelModeStatusBuilder().format_text(status)


def build_and_format_travel_mode_status(
    current_commit: str,
    current_tag: str,
    proof_branch: str,
    bundle_path: str,
    source_of_truth: str = "DESKTOP-K930S6S",
    remote_context: str = "travel_laptop_to_main_pc_remote",
    mode: str = "Travel / Delivery Mode",
    available_components: Optional[List[str]] = None,
    extra_warnings: Optional[List[str]] = None,
) -> str:
    status = build_travel_mode_status(
        current_commit=current_commit,
        current_tag=current_tag,
        proof_branch=proof_branch,
        bundle_path=bundle_path,
        source_of_truth=source_of_truth,
        remote_context=remote_context,
        mode=mode,
        available_components=available_components,
        extra_warnings=extra_warnings,
    )
    return format_travel_mode_status_text(status)
