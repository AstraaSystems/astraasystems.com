"""
response_repairer.py

Phase 2 response repair layer for Arka V1.

This module repairs failed Arka responses after Phase 1 validation.
It does not answer questions independently.
It only repairs specific, known validation failures using trusted context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RepairResult:
    """
    Structured result returned by the response repairer.
    """

    repaired: bool
    response: str
    reason: Optional[str] = None
    applied_repairs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResponseRepairer:
    """
    Repairs failed responses using validator issue codes and trusted context.

    Phase 2 responsibilities:
    - Repair owner identity confusion
    - Repair missing source wording into honest limitation wording
    - Repair unverified action claims into safe non-claim wording
    - Preserve original response when repair is not possible
    """

    def __init__(self, strict_mode: bool = True) -> None:
        self.strict_mode = strict_mode

    def repair(
        self,
        prompt: str,
        response: str,
        issues: List[Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> RepairResult:
        """
        Attempt to repair a failed or warned response.

        issues can be ValidationIssue objects or dictionaries with a "code" key.
        """

        context = context or {}
        issue_codes = self._extract_issue_codes(issues)

        if "OWNER_IDENTITY_CONFUSION" in issue_codes:
            return self._repair_owner_identity(prompt, response, context)

        if "MISSING_SOURCE" in issue_codes:
            return self._repair_missing_source(prompt, response, context)

        if "UNVERIFIED_ACTION_CLAIM" in issue_codes:
            return self._repair_unverified_action_claim(prompt, response, context)

        return RepairResult(
            repaired=False,
            response=response,
            reason="No Phase 2 repair rule matched the validation issues.",
            applied_repairs=[],
            metadata={
                "issue_codes": issue_codes,
            },
        )

    def _extract_issue_codes(self, issues: List[Any]) -> List[str]:
        """
        Extract issue codes from ValidationIssue objects or dictionaries.
        """

        codes: List[str] = []

        for issue in issues:
            if hasattr(issue, "code"):
                codes.append(str(issue.code))
            elif isinstance(issue, dict) and "code" in issue:
                codes.append(str(issue["code"]))

        return codes

    def _repair_owner_identity(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any],
    ) -> RepairResult:
        """
        Repair failed identity answers using trusted owner context.
        """

        owner_name = context.get("owner_name")

        if not owner_name:
            return RepairResult(
                repaired=False,
                response=response,
                reason="Cannot repair owner identity because owner_name is missing.",
                applied_repairs=[],
            )

        repaired_response = f"You are {owner_name}."

        return RepairResult(
            repaired=True,
            response=repaired_response,
            reason="Repaired owner identity response using trusted local context.",
            applied_repairs=["OWNER_IDENTITY_REPAIR"],
            metadata={
                "owner_name_used": owner_name,
            },
        )

    def _repair_missing_source(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any],
    ) -> RepairResult:
        """
        Repair missing-source failures by making the limitation explicit.

        This does not fabricate sources.
        """

        repaired_response = (
            "I do not have a verified source for that answer yet, so I should not "
            "state it as confirmed. Please run the relevant source/tool check first, "
            "then I can answer from verified data."
        )

        return RepairResult(
            repaired=True,
            response=repaired_response,
            reason="Repaired missing-source response into honest limitation wording.",
            applied_repairs=["MISSING_SOURCE_REPAIR"],
        )

    def _repair_unverified_action_claim(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any],
    ) -> RepairResult:
        """
        Repair unverified action claims into safe wording.

        Arka should not claim it sent, deleted, deployed, purchased, or pushed
        anything unless the action is verified by context.
        """

        repaired_response = (
            "I should not claim that action was completed without verification. "
            "I can prepare the command or review the result, but I need execution "
            "proof before saying it was done."
        )

        return RepairResult(
            repaired=True,
            response=repaired_response,
            reason="Repaired unverified action claim into safe non-claim wording.",
            applied_repairs=["UNVERIFIED_ACTION_CLAIM_REPAIR"],
        )


def repair_response(
    prompt: str,
    response: str,
    issues: List[Any],
    context: Optional[Dict[str, Any]] = None,
    strict_mode: bool = True,
) -> RepairResult:
    """
    Convenience function for simple pipeline integration.
    """

    repairer = ResponseRepairer(strict_mode=strict_mode)

    return repairer.repair(
        prompt=prompt,
        response=response,
        issues=issues,
        context=context,
    )
