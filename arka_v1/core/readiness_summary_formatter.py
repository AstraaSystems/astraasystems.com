"""
readiness_summary_formatter.py

Phase 18A readiness-aware user-facing summary formatter for Arka V1.

This module converts safe capability readiness reports into concise,
founder-readable/user-facing summaries.

It consumes data from capability_readiness_reporter.py and does not:
- execute tools
- run shell commands
- call web/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state
- enable capabilities
- fabricate evidence
- expose secrets

Phase 18A is standalone formatting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ReadinessSummaryResult:
    formatted: bool
    summary: str
    capability_name: Optional[str] = None
    status: Optional[str] = None
    missing_requirement_count: Optional[int] = None
    requires_approval: Optional[bool] = None
    allows_mutation: Optional[bool] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "formatted": self.formatted,
            "summary": self.summary,
            "capability_name": self.capability_name,
            "status": self.status,
            "missing_requirement_count": self.missing_requirement_count,
            "requires_approval": self.requires_approval,
            "allows_mutation": self.allows_mutation,
            "metadata": dict(self.metadata),
        }


class ReadinessSummaryFormatter:
    """
    Formats safe capability readiness reports into readable summaries.

    This class does not execute, enable, mutate, or persist anything.
    """

    STATUS_LABELS = {
        "ready": "Ready",
        "not_ready": "Not ready",
        "approval_required": "Approval required",
        "mutation_future_only": "Future mutation only",
        "missing_contract": "Missing enablement contract",
        "unknown": "Unknown",
    }

    def format_capability(
        self,
        readiness: Optional[Dict[str, Any]],
        include_missing_requirements: bool = True,
        max_missing_requirements: int = 5,
    ) -> ReadinessSummaryResult:
        if not readiness:
            return ReadinessSummaryResult(
                formatted=False,
                summary="No readiness report was available for this capability.",
                metadata=self._metadata(),
            )

        capability_name = self._safe_str(readiness.get("capability_name")) or "unknown_capability"
        route = self._safe_str(readiness.get("route")) or "UNKNOWN_ROUTE"
        status = self._safe_str(readiness.get("status")) or "unknown"

        registry_enabled = bool(readiness.get("registry_enabled", False))
        contract_exists = bool(readiness.get("contract_exists", False))
        can_enable = bool(readiness.get("can_enable", False))
        requires_approval = bool(readiness.get("requires_approval", False))
        read_only = bool(readiness.get("read_only", False))
        mutates_state = bool(readiness.get("mutates_state", False))

        missing_requirements = list(readiness.get("missing_requirements", []) or [])
        missing_count = int(readiness.get("missing_requirement_count", len(missing_requirements)) or 0)

        status_label = self.STATUS_LABELS.get(status, "Unknown")

        lines = [
            f"{capability_name}: {status_label}.",
            f"Route: {route}.",
        ]

        if registry_enabled:
            lines.append("Registry state: enabled.")
        else:
            lines.append("Registry state: disabled.")

        if contract_exists:
            lines.append("Enablement contract: present.")
        else:
            lines.append("Enablement contract: missing.")

        if status == "ready":
            lines.append("This capability is contract-ready with the provided safety components.")
        elif status == "not_ready":
            lines.append(
                f"This capability is not ready yet because {missing_count} requirement(s) are missing."
            )
        elif status == "approval_required":
            lines.append(
                f"This capability needs approval before enablement can be considered; {missing_count} requirement(s) are still missing."
            )
        elif status == "mutation_future_only":
            lines.append(
                "This capability belongs to a future mutation-controlled path and must not be enabled through the current read-only path."
            )
        elif status == "missing_contract":
            lines.append(
                "This capability has no matching enablement contract, so it must remain unavailable."
            )
        else:
            lines.append("This capability readiness state is unknown and should remain unavailable.")

        if include_missing_requirements and missing_requirements:
            shown = missing_requirements[:max_missing_requirements]
            lines.append("Missing requirements: " + ", ".join(shown) + ".")
            if len(missing_requirements) > len(shown):
                remaining = len(missing_requirements) - len(shown)
                lines.append(f"Additional missing requirements not shown: {remaining}.")

        if requires_approval:
            lines.append("Approval: required.")

        if mutates_state:
            lines.append("Mutation risk: registry marks this capability as state-mutating.")

        if read_only:
            lines.append("Read-only posture: required or currently read-only.")

        if can_enable and status == "ready":
            lines.append("Safe next step: keep it read-only and evidence-backed before any runtime use.")
        else:
            lines.append("Safe next step: do not enable this capability until its contract requirements are satisfied.")

        return ReadinessSummaryResult(
            formatted=True,
            summary=" ".join(lines),
            capability_name=capability_name,
            status=status,
            missing_requirement_count=missing_count,
            requires_approval=requires_approval,
            allows_mutation=mutates_state or status == "mutation_future_only",
            metadata=self._metadata(),
        )

    def format_all(
        self,
        readiness_reports: List[Dict[str, Any]],
        include_missing_requirements: bool = False,
    ) -> ReadinessSummaryResult:
        reports = readiness_reports or []

        if not reports:
            return ReadinessSummaryResult(
                formatted=False,
                summary="No capability readiness reports were available.",
                metadata=self._metadata(),
            )

        total = len(reports)
        status_counts: Dict[str, int] = {}

        for report in reports:
            status = self._safe_str(report.get("status")) or "unknown"
            status_counts[status] = status_counts.get(status, 0) + 1

        parts = [
            f"Capability readiness summary: {total} capability report(s) reviewed.",
            f"Ready: {status_counts.get('ready', 0)}.",
            f"Not ready: {status_counts.get('not_ready', 0)}.",
            f"Approval required: {status_counts.get('approval_required', 0)}.",
            f"Future mutation only: {status_counts.get('mutation_future_only', 0)}.",
            f"Missing contract: {status_counts.get('missing_contract', 0)}.",
            f"Unknown: {status_counts.get('unknown', 0)}.",
        ]

        if include_missing_requirements:
            blocked = [
                report for report in reports
                if int(report.get("missing_requirement_count", 0) or 0) > 0
            ]
            if blocked:
                names = [
                    self._safe_str(report.get("capability_name")) or "unknown_capability"
                    for report in blocked[:5]
                ]
                parts.append("Capabilities with missing requirements: " + ", ".join(names) + ".")
                if len(blocked) > len(names):
                    parts.append(f"Additional blocked capabilities not shown: {len(blocked) - len(names)}.")

        parts.append(
            "No capabilities were enabled, executed, or mutated by this summary."
        )

        return ReadinessSummaryResult(
            formatted=True,
            summary=" ".join(parts),
            metadata=self._metadata(),
        )

    def format_capability_by_name(
        self,
        capability_name: str,
        available_components: Optional[List[str]] = None,
        include_missing_requirements: bool = True,
    ) -> ReadinessSummaryResult:
        readiness = self._get_readiness(capability_name, available_components)
        return self.format_capability(
            readiness,
            include_missing_requirements=include_missing_requirements,
        )

    def format_all_from_reporter(
        self,
        available_components: Optional[List[str]] = None,
        include_missing_requirements: bool = False,
    ) -> ReadinessSummaryResult:
        reports = self._list_readiness(available_components)
        return self.format_all(
            reports,
            include_missing_requirements=include_missing_requirements,
        )

    def _get_readiness(
        self,
        capability_name: str,
        available_components: Optional[List[str]],
    ) -> Optional[Dict[str, Any]]:
        try:
            try:
                from arka_v1.core.capability_readiness_reporter import get_capability_readiness
            except Exception:
                from core.capability_readiness_reporter import get_capability_readiness

            return get_capability_readiness(
                capability_name,
                available_components=available_components,
            )
        except Exception:
            return None

    def _list_readiness(
        self,
        available_components: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        try:
            try:
                from arka_v1.core.capability_readiness_reporter import list_capability_readiness
            except Exception:
                from core.capability_readiness_reporter import list_capability_readiness

            return list_capability_readiness(
                available_components=available_components,
            )
        except Exception:
            return []

    def _safe_str(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _metadata(self) -> Dict[str, Any]:
        return {
            "formatter_version": "phase18",
            "formatter": "arka_v1.core.readiness_summary_formatter",
            "external_calls": False,
            "memory_mutation": False,
            "tool_execution": False,
            "runtime_writes": False,
            "capability_enablement": False,
            "connector_execution": False,
            "fabricated_results": False,
            "secret_exposure": False,
        }


def format_readiness_summary(
    readiness: Optional[Dict[str, Any]],
    include_missing_requirements: bool = True,
    max_missing_requirements: int = 5,
) -> ReadinessSummaryResult:
    return ReadinessSummaryFormatter().format_capability(
        readiness=readiness,
        include_missing_requirements=include_missing_requirements,
        max_missing_requirements=max_missing_requirements,
    )


def format_capability_readiness_summary(
    capability_name: str,
    available_components: Optional[List[str]] = None,
    include_missing_requirements: bool = True,
) -> ReadinessSummaryResult:
    return ReadinessSummaryFormatter().format_capability_by_name(
        capability_name=capability_name,
        available_components=available_components,
        include_missing_requirements=include_missing_requirements,
    )


def format_all_readiness_summaries(
    available_components: Optional[List[str]] = None,
    include_missing_requirements: bool = False,
) -> ReadinessSummaryResult:
    return ReadinessSummaryFormatter().format_all_from_reporter(
        available_components=available_components,
        include_missing_requirements=include_missing_requirements,
    )
