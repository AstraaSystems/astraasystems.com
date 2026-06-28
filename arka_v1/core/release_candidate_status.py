"""
release_candidate_status.py

Phase 20A Arka V1 Travel Stable / Release Candidate status module.

This module creates a safe, founder-facing release-candidate freeze record
for Arka V1 travel/delivery operation.

It records:
- release candidate identity supplied by caller
- stable commit/tag/proof branch supplied by caller
- stable bundle path supplied by caller
- smoke stack results supplied by caller
- remote operating path supplied by caller
- public website recovery notes supplied by caller
- known follow-up items supplied by caller
- safety boundary metadata

It does not:
- execute shell commands
- inspect Git directly
- mutate Git
- call connectors
- check live websites
- check backend servers
- enable capabilities
- mutate memory
- write runtime state
- expose secrets
- fabricate live status

Phase 20A is standalone release freeze reporting only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


DEFAULT_FREEZE_SCOPE = [
    "Arka V1 response/capability/travel spine through Phase 19.",
    "Travel laptop to DESKTOP-K930S6S remote operating path.",
    "Main PC WSL source-of-truth repo workflow.",
    "Bundle-backed restore path for Phase 17, Phase 18, and Phase 19.",
    "Read-only, evidence-backed capability posture.",
]


DEFAULT_OUT_OF_SCOPE = [
    "New connector execution.",
    "New backend/server health implementation.",
    "New payment/Moneris verification implementation.",
    "New public website deployment architecture.",
    "New capability enablement beyond existing contracts.",
    "Direct Git mutation from Arka runtime.",
]


DEFAULT_SAFETY_BOUNDARIES = [
    "No shell commands are executed by this module.",
    "No Git actions are performed by this module.",
    "No connectors are called by this module.",
    "No capabilities are enabled by this module.",
    "No runtime state is written by this module.",
    "No secrets are copied or exposed by this module.",
    "No live website, payment, backend, or server status is claimed without supplied evidence.",
]


DEFAULT_KNOWN_FOLLOWUPS = [
    "Backend/API remains a separate operational follow-up if tools require live server routes.",
    "Public /api/health previously returned GitHub Pages 404 and should not be claimed healthy without verified evidence.",
    "Local backend ports previously returned connection refused and should not be claimed running without verified evidence.",
]


@dataclass
class ReleaseCandidateStatus:
    release_name: str
    mode: str
    current_commit: str
    stable_tag: str
    proof_branch: str
    bundle_path: str
    source_of_truth: str
    remote_context: str
    smoke_stack_passed: bool
    smoke_stack_summary: List[str] = field(default_factory=list)
    freeze_scope: List[str] = field(default_factory=list)
    out_of_scope: List[str] = field(default_factory=list)
    safety_boundaries: List[str] = field(default_factory=list)
    website_recovery_notes: List[str] = field(default_factory=list)
    known_followups: List[str] = field(default_factory=list)
    release_decision: str = ""
    next_safe_action: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "release_name": self.release_name,
            "mode": self.mode,
            "current_commit": self.current_commit,
            "stable_tag": self.stable_tag,
            "proof_branch": self.proof_branch,
            "bundle_path": self.bundle_path,
            "source_of_truth": self.source_of_truth,
            "remote_context": self.remote_context,
            "smoke_stack_passed": self.smoke_stack_passed,
            "smoke_stack_summary": list(self.smoke_stack_summary),
            "freeze_scope": list(self.freeze_scope),
            "out_of_scope": list(self.out_of_scope),
            "safety_boundaries": list(self.safety_boundaries),
            "website_recovery_notes": list(self.website_recovery_notes),
            "known_followups": list(self.known_followups),
            "release_decision": self.release_decision,
            "next_safe_action": self.next_safe_action,
            "metadata": dict(self.metadata),
        }


class ReleaseCandidateStatusBuilder:
    """
    Builds a Phase 20 release-candidate freeze record.

    This builder only formats supplied evidence. It does not inspect the system,
    execute tools, mutate files, or verify live services.
    """

    def build(
        self,
        current_commit: str,
        stable_tag: str,
        proof_branch: str,
        bundle_path: str,
        smoke_stack_passed: bool,
        release_name: str = "Arka V1 Travel Stable Release Candidate",
        mode: str = "Travel Stable / Release Candidate Freeze",
        source_of_truth: str = "DESKTOP-K930S6S",
        remote_context: str = "Langford travel laptop to main PC remote",
        smoke_stack_summary: Optional[List[str]] = None,
        website_recovery_notes: Optional[List[str]] = None,
        known_followups: Optional[List[str]] = None,
        freeze_scope: Optional[List[str]] = None,
        out_of_scope: Optional[List[str]] = None,
        safety_boundaries: Optional[List[str]] = None,
    ) -> ReleaseCandidateStatus:
        smoke_summary = list(smoke_stack_summary or [])
        site_notes = list(website_recovery_notes or [])
        followups = list(DEFAULT_KNOWN_FOLLOWUPS)
        for item in known_followups or []:
            if item and item not in followups:
                followups.append(str(item))

        scope = list(freeze_scope or DEFAULT_FREEZE_SCOPE)
        exclusions = list(out_of_scope or DEFAULT_OUT_OF_SCOPE)
        boundaries = list(safety_boundaries or DEFAULT_SAFETY_BOUNDARIES)

        release_decision = (
            "release_candidate_ready"
            if smoke_stack_passed
            else "release_candidate_blocked"
        )

        next_safe_action = (
            "Create the Phase 20 smoke proof and final travel-stable bundle."
            if smoke_stack_passed
            else "Resolve failed smoke evidence before creating a release-candidate tag."
        )

        return ReleaseCandidateStatus(
            release_name=self._safe_str(release_name) or "Arka V1 Travel Stable Release Candidate",
            mode=self._safe_str(mode) or "Travel Stable / Release Candidate Freeze",
            current_commit=self._safe_str(current_commit) or "unknown_commit",
            stable_tag=self._safe_str(stable_tag) or "unknown_stable_tag",
            proof_branch=self._safe_str(proof_branch) or "unknown_proof_branch",
            bundle_path=self._safe_str(bundle_path) or "unknown_bundle_path",
            source_of_truth=self._safe_str(source_of_truth) or "DESKTOP-K930S6S",
            remote_context=self._safe_str(remote_context) or "unknown_remote_context",
            smoke_stack_passed=bool(smoke_stack_passed),
            smoke_stack_summary=smoke_summary,
            freeze_scope=scope,
            out_of_scope=exclusions,
            safety_boundaries=boundaries,
            website_recovery_notes=site_notes,
            known_followups=followups,
            release_decision=release_decision,
            next_safe_action=next_safe_action,
            metadata=self._metadata(),
        )

    def format_text(self, status: ReleaseCandidateStatus) -> str:
        lines = [
            "Arka V1 Travel Stable Release Candidate Status",
            "",
            f"Release name: {status.release_name}",
            f"Mode: {status.mode}",
            f"Current commit: {status.current_commit}",
            f"Stable tag: {status.stable_tag}",
            f"Proof branch: {status.proof_branch}",
            f"Bundle: {status.bundle_path}",
            f"Source of truth: {status.source_of_truth}",
            f"Remote context: {status.remote_context}",
            f"Smoke stack passed: {status.smoke_stack_passed}",
            f"Release decision: {status.release_decision}",
            "",
            "Smoke stack summary:",
        ]

        if status.smoke_stack_summary:
            for item in status.smoke_stack_summary:
                lines.append(f"- {item}")
        else:
            lines.append("- No smoke stack summary was supplied.")

        lines.append("")
        lines.append("Freeze scope:")
        for item in status.freeze_scope:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Out of scope:")
        for item in status.out_of_scope:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Safety boundaries:")
        for item in status.safety_boundaries:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Website recovery notes:")
        if status.website_recovery_notes:
            for item in status.website_recovery_notes:
                lines.append(f"- {item}")
        else:
            lines.append("- No website recovery notes were supplied.")

        lines.append("")
        lines.append("Known follow-ups:")
        for item in status.known_followups:
            lines.append(f"- {item}")

        lines.extend([
            "",
            f"Next safe action: {status.next_safe_action}",
            "",
            "No shell commands, Git actions, connectors, runtime state, capabilities, secrets, or live service checks were executed by this release-candidate status module.",
        ])

        return "\n".join(lines)

    def _safe_str(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _metadata(self) -> Dict[str, Any]:
        return {
            "status_version": "phase20",
            "module": "arka_v1.core.release_candidate_status",
            "external_calls": False,
            "shell_execution": False,
            "git_mutation": False,
            "memory_mutation": False,
            "runtime_writes": False,
            "tool_execution": False,
            "connector_execution": False,
            "capability_enablement": False,
            "live_service_checks": False,
            "secret_exposure": False,
            "fabricated_results": False,
        }


def build_release_candidate_status(
    current_commit: str,
    stable_tag: str,
    proof_branch: str,
    bundle_path: str,
    smoke_stack_passed: bool,
    release_name: str = "Arka V1 Travel Stable Release Candidate",
    mode: str = "Travel Stable / Release Candidate Freeze",
    source_of_truth: str = "DESKTOP-K930S6S",
    remote_context: str = "Langford travel laptop to main PC remote",
    smoke_stack_summary: Optional[List[str]] = None,
    website_recovery_notes: Optional[List[str]] = None,
    known_followups: Optional[List[str]] = None,
    freeze_scope: Optional[List[str]] = None,
    out_of_scope: Optional[List[str]] = None,
    safety_boundaries: Optional[List[str]] = None,
) -> ReleaseCandidateStatus:
    return ReleaseCandidateStatusBuilder().build(
        current_commit=current_commit,
        stable_tag=stable_tag,
        proof_branch=proof_branch,
        bundle_path=bundle_path,
        smoke_stack_passed=smoke_stack_passed,
        release_name=release_name,
        mode=mode,
        source_of_truth=source_of_truth,
        remote_context=remote_context,
        smoke_stack_summary=smoke_stack_summary,
        website_recovery_notes=website_recovery_notes,
        known_followups=known_followups,
        freeze_scope=freeze_scope,
        out_of_scope=out_of_scope,
        safety_boundaries=safety_boundaries,
    )


def format_release_candidate_status_text(status: ReleaseCandidateStatus) -> str:
    return ReleaseCandidateStatusBuilder().format_text(status)


def build_and_format_release_candidate_status(
    current_commit: str,
    stable_tag: str,
    proof_branch: str,
    bundle_path: str,
    smoke_stack_passed: bool,
    release_name: str = "Arka V1 Travel Stable Release Candidate",
    mode: str = "Travel Stable / Release Candidate Freeze",
    source_of_truth: str = "DESKTOP-K930S6S",
    remote_context: str = "Langford travel laptop to main PC remote",
    smoke_stack_summary: Optional[List[str]] = None,
    website_recovery_notes: Optional[List[str]] = None,
    known_followups: Optional[List[str]] = None,
    freeze_scope: Optional[List[str]] = None,
    out_of_scope: Optional[List[str]] = None,
    safety_boundaries: Optional[List[str]] = None,
) -> str:
    status = build_release_candidate_status(
        current_commit=current_commit,
        stable_tag=stable_tag,
        proof_branch=proof_branch,
        bundle_path=bundle_path,
        smoke_stack_passed=smoke_stack_passed,
        release_name=release_name,
        mode=mode,
        source_of_truth=source_of_truth,
        remote_context=remote_context,
        smoke_stack_summary=smoke_stack_summary,
        website_recovery_notes=website_recovery_notes,
        known_followups=known_followups,
        freeze_scope=freeze_scope,
        out_of_scope=out_of_scope,
        safety_boundaries=safety_boundaries,
    )
    return format_release_candidate_status_text(status)
