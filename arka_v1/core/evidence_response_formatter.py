"""
evidence_response_formatter.py

Phase 8A evidence response formatter for Arka V1.

Formats already-collected source evidence into clearer final responses.

It does not:
- execute tools
- call web/search/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state
- fabricate evidence
- create fake citations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re


@dataclass
class FormatResult:
    formatted: bool
    response: str
    used_evidence: bool = False
    evidence_types: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EvidenceResponseFormatter:
    """
    Formats source evidence into human-readable responses.

    Phase 8A supports local Git evidence only.
    """

    def format(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> FormatResult:
        context = context or {}
        source_results = context.get("source_results", []) or []
        source_execution = context.get("source_execution", {}) or {}
        source_route = context.get("source_route", {}) or {}

        git_results = [
            item for item in source_results
            if isinstance(item, dict) and item.get("source") == "local_git"
        ]

        if not git_results:
            return FormatResult(
                formatted=False,
                response=response,
                used_evidence=False,
                reason="No local_git evidence available for formatting.",
                metadata=self._metadata(source_route, source_execution),
            )

        item = git_results[0]
        evidence_type = str(item.get("type", "") or "")
        content = str(item.get("content", "") or "")
        command = (item.get("metadata", {}) or {}).get("command", [])

        if evidence_type == "git_status_branch":
            return self._format_git_status_branch(content, command, source_route, source_execution)

        if evidence_type == "git_branch_current":
            return self._finish(
                f"Current branch: {content.strip() or 'unknown'}.",
                "git_branch_current",
                command,
                "Formatted current Git branch evidence.",
                source_route,
                source_execution,
            )

        if evidence_type == "git_log_recent":
            return self._format_git_log_recent(content, command, source_route, source_execution)

        if evidence_type == "git_remote_verbose":
            return self._format_git_remote_verbose(content, command, source_route, source_execution)

        if evidence_type == "git_status_short":
            return self._format_git_status_short(content, command, source_route, source_execution)

        return FormatResult(
            formatted=False,
            response=response,
            used_evidence=False,
            evidence_types=[evidence_type],
            sources=["local_git"],
            reason=f"No Phase 8A formatter matched evidence type: {evidence_type}",
            metadata=self._metadata(source_route, source_execution),
        )

    def _metadata(self, source_route: Dict[str, Any], source_execution: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "formatter_version": "phase8",
            "formatter": "arka_v1.core.evidence_response_formatter",
            "external_calls": False,
            "memory_mutation": False,
            "tool_execution": False,
            "source_route": dict(source_route),
            "source_execution_status": source_execution.get("status"),
            "source_execution_executed": source_execution.get("executed"),
        }

    def _source_line(self, command: Any) -> str:
        if isinstance(command, list) and command:
            command_text = " ".join(str(part) for part in command)
        elif command:
            command_text = str(command)
        else:
            command_text = "local Git evidence"

        return f"Source: local_git / {command_text}"

    def _finish(
        self,
        body: str,
        evidence_type: str,
        command: Any,
        reason: str,
        source_route: Dict[str, Any],
        source_execution: Dict[str, Any],
    ) -> FormatResult:
        response = body.rstrip() + "\n\n" + self._source_line(command)

        return FormatResult(
            formatted=True,
            response=response,
            used_evidence=True,
            evidence_types=[evidence_type],
            sources=["local_git"],
            reason=reason,
            metadata=self._metadata(source_route, source_execution),
        )

    def _format_git_status_branch(
        self,
        content: str,
        command: Any,
        source_route: Dict[str, Any],
        source_execution: Dict[str, Any],
    ) -> FormatResult:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        branch_line = lines[0] if lines else ""

        branch = None
        upstream = None
        ahead = None
        behind = None

        match = re.match(
            r"^##\s+([^\.\s]+)(?:\.\.\.([^\s\[]+))?(?:\s+\[(.*?)\])?",
            branch_line,
        )

        if match:
            branch = match.group(1)
            upstream = match.group(2)
            tracking_info = match.group(3) or ""

            ahead_match = re.search(r"ahead\s+(\d+)", tracking_info)
            behind_match = re.search(r"behind\s+(\d+)", tracking_info)

            if ahead_match:
                ahead = ahead_match.group(1)

            if behind_match:
                behind = behind_match.group(1)

        response_lines: List[str] = []

        if branch:
            if upstream:
                response_lines.append(f"You are on branch {branch}, tracking {upstream}.")
            else:
                response_lines.append(f"You are on branch {branch}.")

            status_parts = []

            if ahead:
                status_parts.append(f"ahead by {ahead} commit{'s' if ahead != '1' else ''}")

            if behind:
                status_parts.append(f"behind by {behind} commit{'s' if behind != '1' else ''}")

            if status_parts:
                response_lines.append("Your local branch is " + " and ".join(status_parts) + ".")

            if len(lines) == 1:
                response_lines.append("No file changes were shown in the captured status output.")
            elif len(lines) > 1:
                response_lines.append("The captured status output also includes file-level changes.")
        else:
            response_lines.append("Git status evidence was captured.")
            if content:
                response_lines.append(content)

        return self._finish(
            "\n".join(response_lines),
            "git_status_branch",
            command,
            "Formatted git status branch evidence.",
            source_route,
            source_execution,
        )

    def _format_git_log_recent(
        self,
        content: str,
        command: Any,
        source_route: Dict[str, Any],
        source_execution: Dict[str, Any],
    ) -> FormatResult:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        response_lines = ["Recent commits:"]

        if lines:
            for line in lines[:10]:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    response_lines.append(f"- {parts[0]} — {parts[1]}")
                else:
                    response_lines.append(f"- {line}")
        else:
            response_lines.append("- No recent commit lines were shown in the captured evidence.")

        return self._finish(
            "\n".join(response_lines),
            "git_log_recent",
            command,
            "Formatted recent Git log evidence.",
            source_route,
            source_execution,
        )

    def _format_git_remote_verbose(
        self,
        content: str,
        command: Any,
        source_route: Dict[str, Any],
        source_execution: Dict[str, Any],
    ) -> FormatResult:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        response_lines = ["Configured Git remotes:"]

        if lines:
            for line in lines:
                response_lines.append(f"- {line}")
        else:
            response_lines.append("- No remotes were shown in the captured evidence.")

        return self._finish(
            "\n".join(response_lines),
            "git_remote_verbose",
            command,
            "Formatted Git remote evidence.",
            source_route,
            source_execution,
        )

    def _format_git_status_short(
        self,
        content: str,
        command: Any,
        source_route: Dict[str, Any],
        source_execution: Dict[str, Any],
    ) -> FormatResult:
        lines = [line.rstrip() for line in content.splitlines() if line.strip()]

        if lines:
            response_lines = ["Git working tree changes shown in captured evidence:"]
            for line in lines:
                response_lines.append(f"- {line}")
        else:
            response_lines = ["No working tree changes were shown in the captured short status output."]

        return self._finish(
            "\n".join(response_lines),
            "git_status_short",
            command,
            "Formatted short Git status evidence.",
            source_route,
            source_execution,
        )


def format_response_with_evidence(
    prompt: str,
    response: str,
    context: Optional[Dict[str, Any]] = None,
) -> FormatResult:
    formatter = EvidenceResponseFormatter()
    return formatter.format(prompt=prompt, response=response, context=context)
