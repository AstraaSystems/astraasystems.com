"""
source_execution_bridge.py

Phase 7A source/tool execution bridge for Arka V1.

This module turns Phase 6 source_route decisions into safe read-only evidence
collection where possible.

It does not:
- execute destructive commands
- push, commit, deploy, delete, send, submit, purchase, or mutate anything
- write memory or runtime state
- call payment systems
- call production mutation endpoints

Phase 7A is intentionally conservative:
- local profile and general knowledge routes do not execute external tools
- Git/GitHub route supports limited read-only local Git evidence only
- web/Astraa/server/payment routes return structured "not implemented yet" results
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import subprocess


READ_ONLY_GIT_COMMANDS: Dict[str, List[str]] = {
    "git_status_short": ["git", "status", "--short"],
    "git_status_branch": ["git", "status", "-sb"],
    "git_branch_current": ["git", "branch", "--show-current"],
    "git_log_recent": ["git", "--no-pager", "log", "--oneline", "--decorate", "-10"],
    "git_remote_verbose": ["git", "remote", "-v"],
}


UNSAFE_ACTION_TERMS = [
    " push ",
    " pushed ",
    " commit ",
    " committed ",
    " tag ",
    " tagged ",
    " deploy ",
    " deployed ",
    " delete ",
    " deleted ",
    " send ",
    " sent ",
    " submit ",
    " submitted ",
    " purchase ",
    " purchased ",
    " install ",
    " installed ",
    " move ",
    " moved ",
    " rename ",
    " renamed ",
    " reset ",
    " restore ",
    " clean ",
    " checkout ",
    " merge ",
    " rebase ",
]


@dataclass
class SourceEvidence:
    """
    Normalized source evidence item.
    """

    type: str
    source: str
    content: str
    trusted: bool = True
    read_only: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "source": self.source,
            "content": self.content,
            "trusted": self.trusted,
            "read_only": self.read_only,
            "metadata": dict(self.metadata),
        }


@dataclass
class SourceExecutionResult:
    """
    Structured result returned by Phase 7 source/tool execution bridge.
    """

    executed: bool
    route: str
    source_type: Optional[str]
    status: str
    message: str
    evidence: List[SourceEvidence] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    source_results: List[Dict[str, Any]] = field(default_factory=list)
    verified_actions: List[str] = field(default_factory=list)
    blocked_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "executed": self.executed,
            "route": self.route,
            "source_type": self.source_type,
            "status": self.status,
            "message": self.message,
            "evidence": [item.to_dict() for item in self.evidence],
            "sources": list(self.sources),
            "source_results": list(self.source_results),
            "verified_actions": list(self.verified_actions),
            "blocked_reason": self.blocked_reason,
            "metadata": dict(self.metadata),
        }


class SourceExecutionBridge:
    """
    Phase 7A source/tool execution bridge.

    This bridge executes only safe read-only evidence collection.
    """

    def __init__(self, repo_root: Optional[str | Path] = None) -> None:
        self.repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()

    def execute(
        self,
        prompt: str,
        context: Dict[str, Any],
    ) -> SourceExecutionResult:
        """
        Execute a safe source/tool evidence route if allowed.
        """

        source_route = context.get("source_route", {}) or {}
        route = str(source_route.get("route", "UNKNOWN"))
        source_type = source_route.get("source_type")

        normalized_prompt = self._normalize_prompt(prompt)

        if route in {"LOCAL_PROFILE", "GENERAL_KNOWLEDGE", "MATH_REQUIRED", "UNKNOWN"}:
            return self._no_execution_needed(route, source_type)

        if route == "GITHUB_REQUIRED":
            return self._execute_git_read_only_route(normalized_prompt, route, source_type)

        if route in {
            "WEB_SOURCE_REQUIRED",
            "ASTRAA_STATUS_REQUIRED",
            "SERVER_REQUIRED",
            "PAYMENT_REQUIRED",
        }:
            return self._not_implemented_yet(route, source_type)

        if route == "ACTION_VERIFICATION_REQUIRED":
            return self._blocked_action_verification(route, source_type)

        return self._not_implemented_yet(route, source_type)

    def _normalize_prompt(self, prompt: str) -> str:
        """
        Normalize prompt for conservative routing checks.
        """

        return f" {(prompt or '').strip().lower()} "

    def _metadata(self) -> Dict[str, Any]:
        return {
            "bridge_version": "phase7",
            "bridge": "arka_v1.core.source_execution_bridge",
            "read_only": True,
            "mutated_state": False,
            "tool_execution": "safe_read_only_only",
            "repo_root": str(self.repo_root),
        }

    def _no_execution_needed(
        self,
        route: str,
        source_type: Optional[str],
    ) -> SourceExecutionResult:
        """
        Return no-op result for routes that do not require external evidence execution.
        """

        return SourceExecutionResult(
            executed=False,
            route=route,
            source_type=source_type,
            status="not_required",
            message="No source/tool execution required for this route.",
            evidence=[],
            sources=[],
            source_results=[],
            verified_actions=[],
            metadata=self._metadata(),
        )

    def _not_implemented_yet(
        self,
        route: str,
        source_type: Optional[str],
    ) -> SourceExecutionResult:
        """
        Return structured non-execution for routes that Phase 7A does not execute yet.
        """

        return SourceExecutionResult(
            executed=False,
            route=route,
            source_type=source_type,
            status="not_implemented",
            message=(
                "This source route is recognized, but Phase 7A does not execute "
                "this connector yet."
            ),
            evidence=[],
            sources=[],
            source_results=[],
            verified_actions=[],
            blocked_reason="connector_not_implemented_in_phase7a",
            metadata=self._metadata(),
        )

    def _blocked_action_verification(
        self,
        route: str,
        source_type: Optional[str],
    ) -> SourceExecutionResult:
        """
        Block action-verification execution in Phase 7A.
        """

        return SourceExecutionResult(
            executed=False,
            route=route,
            source_type=source_type,
            status="blocked",
            message=(
                "Action verification requires execution evidence, but Phase 7A "
                "only allows read-only evidence collection."
            ),
            evidence=[],
            sources=[],
            source_results=[],
            verified_actions=[],
            blocked_reason="action_verification_not_allowed_in_phase7a",
            metadata=self._metadata(),
        )

    def _execute_git_read_only_route(
        self,
        normalized_prompt: str,
        route: str,
        source_type: Optional[str],
    ) -> SourceExecutionResult:
        """
        Execute safe read-only Git evidence collection.

        Unsafe action-like prompts are blocked even under GITHUB_REQUIRED.
        """

        if self._contains_unsafe_action(normalized_prompt):
            return SourceExecutionResult(
                executed=False,
                route=route,
                source_type=source_type,
                status="blocked",
                message=(
                    "Git/GitHub route detected an action-like prompt. Phase 7A "
                    "does not execute push, commit, deploy, reset, merge, or other "
                    "state-changing commands."
                ),
                evidence=[],
                sources=[],
                source_results=[],
                verified_actions=[],
                blocked_reason="unsafe_git_action_blocked",
                metadata=self._metadata(),
            )

        command_key = self._select_git_read_only_command(normalized_prompt)
        command = READ_ONLY_GIT_COMMANDS[command_key]

        try:
            completed = subprocess.run(
                command,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
        except Exception as exc:
            return SourceExecutionResult(
                executed=False,
                route=route,
                source_type=source_type,
                status="error",
                message=f"Read-only Git command failed before completion: {exc}",
                evidence=[],
                sources=[],
                source_results=[],
                verified_actions=[],
                blocked_reason="git_command_exception",
                metadata={
                    **self._metadata(),
                    "command_key": command_key,
                    "command": command,
                },
            )

        output = (completed.stdout or "").strip()
        error = (completed.stderr or "").strip()

        content = output if output else error

        evidence = SourceEvidence(
            type=command_key,
            source="local_git",
            content=content,
            trusted=True,
            read_only=True,
            metadata={
                "command": command,
                "returncode": completed.returncode,
            },
        )

        source_result = evidence.to_dict()

        return SourceExecutionResult(
            executed=True,
            route=route,
            source_type=source_type,
            status="success" if completed.returncode == 0 else "error",
            message="Collected read-only Git evidence.",
            evidence=[evidence],
            sources=["local_git"],
            source_results=[source_result],
            verified_actions=[],
            blocked_reason=None if completed.returncode == 0 else "git_command_returned_error",
            metadata={
                **self._metadata(),
                "command_key": command_key,
                "command": command,
                "returncode": completed.returncode,
            },
        )

    def _contains_unsafe_action(self, normalized_prompt: str) -> bool:
        """
        Detect action-like prompts that Phase 7A must not execute.
        """

        return any(term in normalized_prompt for term in UNSAFE_ACTION_TERMS)

    def _select_git_read_only_command(self, normalized_prompt: str) -> str:
        """
        Select a predefined read-only Git command.
        """

        if " branch " in normalized_prompt or "what branch" in normalized_prompt:
            return "git_branch_current"

        if " remote " in normalized_prompt or " origin " in normalized_prompt:
            return "git_remote_verbose"

        if " log " in normalized_prompt or " commits " in normalized_prompt:
            return "git_log_recent"

        if "status -sb" in normalized_prompt or "ahead" in normalized_prompt:
            return "git_status_branch"

        return "git_status_branch"


def execute_source_route(
    prompt: str,
    context: Dict[str, Any],
    repo_root: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """
    Convenience function for source route execution.
    """

    bridge = SourceExecutionBridge(repo_root=repo_root)
    return bridge.execute(prompt=prompt, context=context).to_dict()


def merge_source_execution(
    context: Dict[str, Any],
    execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merge source execution evidence into an Arka context dictionary.

    This returns a new dictionary and does not mutate the original context.
    """

    merged = dict(context)

    existing_sources = list(merged.get("sources", []))
    existing_results = list(merged.get("source_results", []))
    existing_verified_actions = list(merged.get("verified_actions", []))

    new_sources = list(execution_result.get("sources", []))
    new_results = list(execution_result.get("source_results", []))
    new_verified_actions = list(execution_result.get("verified_actions", []))

    merged["sources"] = existing_sources + [
        source for source in new_sources if source not in existing_sources
    ]
    merged["source_results"] = existing_results + new_results
    merged["verified_actions"] = existing_verified_actions + [
        action for action in new_verified_actions if action not in existing_verified_actions
    ]
    merged["source_execution"] = dict(execution_result)

    metadata = dict(merged.get("metadata", {}))
    metadata.update(
        {
            "source_execution_bridge": "phase7",
            "source_execution_status": execution_result.get("status"),
            "source_execution_executed": execution_result.get("executed"),
        }
    )
    merged["metadata"] = metadata

    return merged
