"""
response_validator.py

Phase 1 response validation layer for Arka V1.

This module validates Arka responses before they are returned to the owner.
It does not answer questions directly.
It only reviews generated responses for safety, grounding, clarity, and integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import re


class ValidationStatus(str, Enum):
    """
    Validation outcome for an Arka response.
    """

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class ValidationIssue:
    """
    Represents a single validation issue found in a generated response.
    """

    code: str
    message: str
    severity: str = "warn"
    field: Optional[str] = None


@dataclass
class ValidationResult:
    """
    Structured result returned by the response validator.
    """

    status: ValidationStatus
    response: str
    issues: List[ValidationIssue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == ValidationStatus.PASS


class ResponseValidator:
    """
    Central validator for Arka-generated responses.

    Phase 1 responsibilities:
    - Detect empty responses
    - Protect owner identity responses
    - Detect overconfident unsupported claims
    - Require sources when context says sources are needed
    - Prevent unverified action-completed claims
    - Flag vague or low-quality responses
    """

    def __init__(self, strict_mode: bool = True) -> None:
        self.strict_mode = strict_mode

    def validate(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Validate a generated response before it is returned to the owner.
        """

        context = context or {}
        issues: List[ValidationIssue] = []

        issues.extend(self._check_empty_response(response))
        issues.extend(self._check_owner_identity(prompt, response, context))
        issues.extend(self._check_overconfidence(response, context))
        issues.extend(self._check_source_grounding(response, context))
        issues.extend(self._check_unsafe_actions(response, context))
        issues.extend(self._check_clarity(response))

        status = self._determine_status(issues)

        return ValidationResult(
            status=status,
            response=response,
            issues=issues,
            metadata={
                "strict_mode": self.strict_mode,
                "issue_count": len(issues),
            },
        )

    def _check_empty_response(self, response: str) -> List[ValidationIssue]:
        """
        Fail if the generated response is empty.
        """

        if not response or not response.strip():
            return [
                ValidationIssue(
                    code="EMPTY_RESPONSE",
                    message="Response is empty.",
                    severity="fail",
                )
            ]

        return []

    def _check_owner_identity(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any],
    ) -> List[ValidationIssue]:
        """
        Ensure identity questions use known local owner identity when available.
        """

        issues: List[ValidationIssue] = []

        normalized_prompt = prompt.lower().strip()

        identity_questions = {
            "who am i",
            "who am i?",
            "what is my name",
            "what is my name?",
            "identify me",
            "identify me?",
        }

        if normalized_prompt in identity_questions:
            owner_name = context.get("owner_name")

            if owner_name and owner_name.lower() not in response.lower():
                issues.append(
                    ValidationIssue(
                        code="OWNER_IDENTITY_CONFUSION",
                        message=(
                            "Identity question did not use known owner identity "
                            "from local context."
                        ),
                        severity="fail",
                    )
                )

            if not owner_name:
                issues.append(
                    ValidationIssue(
                        code="OWNER_IDENTITY_MISSING_CONTEXT",
                        message="Identity question was asked but owner_name was missing from context.",
                        severity="warn",
                    )
                )

        return issues

    def _check_overconfidence(
        self,
        response: str,
        context: Dict[str, Any],
    ) -> List[ValidationIssue]:
        """
        Warn when response uses overly certain language without source context.
        """

        issues: List[ValidationIssue] = []

        risky_phrases = [
            "definitely",
            "guaranteed",
            "without a doubt",
            "100%",
            "certainly",
            "absolutely certain",
        ]

        has_sources = bool(context.get("sources"))
        lower_response = response.lower()

        if not has_sources:
            for phrase in risky_phrases:
                if phrase in lower_response:
                    issues.append(
                        ValidationIssue(
                            code="OVERCONFIDENT_RESPONSE",
                            message=(
                                "Response uses overconfident language without "
                                f"sources: {phrase}"
                            ),
                            severity="warn",
                        )
                    )

        return issues

    def _check_source_grounding(
        self,
        response: str,
        context: Dict[str, Any],
    ) -> List[ValidationIssue]:
        """
        Require source context when the caller marks the response as source-required.
        """

        issues: List[ValidationIssue] = []

        requires_source = bool(context.get("requires_source", False))
        sources = context.get("sources", [])

        if requires_source and not sources:
            issues.append(
                ValidationIssue(
                    code="MISSING_SOURCE",
                    message="Response requires a source but no source was provided.",
                    severity="fail" if self.strict_mode else "warn",
                )
            )

        return issues

    def _check_unsafe_actions(
        self,
        response: str,
        context: Dict[str, Any],
    ) -> List[ValidationIssue]:
        """
        Prevent Arka from claiming actions were completed unless context verifies execution.
        """

        issues: List[ValidationIssue] = []

        verified_actions = set(context.get("verified_actions", []))

        claimed_action_patterns = {
            "sent": r"\bi sent\b",
            "purchased": r"\bi purchased\b",
            "deleted": r"\bi deleted\b",
            "transferred": r"\bi transferred\b",
            "submitted": r"\bi submitted\b",
            "signed": r"\bi signed\b",
            "deployed": r"\bi deployed\b",
            "installed": r"\bi installed\b",
            "committed": r"\bi committed\b",
            "pushed": r"\bi pushed\b",
        }

        lower_response = response.lower()

        for action_name, pattern in claimed_action_patterns.items():
            if re.search(pattern, lower_response) and action_name not in verified_actions:
                issues.append(
                    ValidationIssue(
                        code="UNVERIFIED_ACTION_CLAIM",
                        message=(
                            "Response appears to claim an action was completed "
                            f"without verification: {action_name}"
                        ),
                        severity="fail",
                    )
                )

        return issues

    def _check_clarity(self, response: str) -> List[ValidationIssue]:
        """
        Flag very short or vague responses.
        """

        issues: List[ValidationIssue] = []

        stripped = response.strip()

        if len(stripped) < 3:
            issues.append(
                ValidationIssue(
                    code="TOO_SHORT",
                    message="Response is too short to be useful.",
                    severity="warn",
                )
            )

        vague_phrases = [
            "something went wrong",
            "i don't know",
            "not sure",
            "cannot help",
            "no information available",
        ]

        lower_response = response.lower()

        for phrase in vague_phrases:
            if phrase in lower_response:
                issues.append(
                    ValidationIssue(
                        code="VAGUE_RESPONSE",
                        message=f"Response contains vague phrase: {phrase}",
                        severity="warn",
                    )
                )

        return issues

    def _determine_status(
        self,
        issues: List[ValidationIssue],
    ) -> ValidationStatus:
        """
        Convert validation issues into a final validation status.
        """

        if any(issue.severity == "fail" for issue in issues):
            return ValidationStatus.FAIL

        if issues:
            return ValidationStatus.WARN

        return ValidationStatus.PASS


def validate_response(
    prompt: str,
    response: str,
    context: Optional[Dict[str, Any]] = None,
    strict_mode: bool = True,
) -> ValidationResult:
    """
    Convenience function for simple pipeline integration.
    """

    validator = ResponseValidator(strict_mode=strict_mode)
    return validator.validate(
        prompt=prompt,
        response=response,
        context=context,
    )
