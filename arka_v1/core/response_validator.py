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
        issues.extend(self._check_family_identity(prompt, response, context))
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

    def _check_family_identity(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any],
    ) -> List[ValidationIssue]:
        """
        ARKA_FAMILY_IDENTITY_VALIDATOR_PHASE5A

        Ensure family identity questions use trusted profile-backed context.

        This check is intentionally conservative:
        - It only applies when the context flags a family identity question.
        - It only fails when the trusted family profile contains the expected answer.
        - It does not call web/search or mutate memory.
        """

        issues: List[ValidationIssue] = []

        prompt_flags = context.get("prompt_flags", {})
        is_family_identity_question = bool(
            prompt_flags.get("is_family_identity_question", False)
        )

        if not is_family_identity_question:
            return issues

        normalized_prompt = prompt.lower().strip()
        lower_response = response.lower()
        family = context.get("family", {})

        wife_name = str(family.get("wife_name", "")).strip()
        son_name = str(family.get("first_born_son_name", "")).strip()

        asks_about_wife = self._prompt_asks_about_wife(normalized_prompt)
        asks_about_son = self._prompt_asks_about_son(normalized_prompt)

        if asks_about_wife:
            if not wife_name:
                issues.append(
                    ValidationIssue(
                        code="FAMILY_IDENTITY_MISSING_CONTEXT_WIFE",
                        message="Family identity question asked about wife, but wife_name was missing from context.",
                        severity="warn",
                    )
                )
            elif wife_name.lower() not in lower_response:
                issues.append(
                    ValidationIssue(
                        code="FAMILY_IDENTITY_CONFUSION_WIFE",
                        message="Family identity question did not use trusted wife_name from profile-backed context.",
                        severity="fail",
                    )
                )

        if asks_about_son:
            if not son_name:
                issues.append(
                    ValidationIssue(
                        code="FAMILY_IDENTITY_MISSING_CONTEXT_SON",
                        message="Family identity question asked about son, but first_born_son_name was missing from context.",
                        severity="warn",
                    )
                )
            elif son_name.lower() not in lower_response:
                issues.append(
                    ValidationIssue(
                        code="FAMILY_IDENTITY_CONFUSION_SON",
                        message="Family identity question did not use trusted first_born_son_name from profile-backed context.",
                        severity="fail",
                    )
                )

        if not asks_about_wife and not asks_about_son:
            issues.append(
                ValidationIssue(
                    code="FAMILY_IDENTITY_UNCLASSIFIED",
                    message="Family identity question was detected, but validator could not classify wife or son target.",
                    severity="warn",
                )
            )

        return issues

    def _prompt_asks_about_wife(self, text: str) -> bool:
        """
        Detect wife-name questions.
        """

        wife_terms = [
            "wife",
            "wife's name",
            "wifes name",
            "my wife's name",
            "my wife name",
        ]

        return any(term in text for term in wife_terms)

    def _prompt_asks_about_son(self, text: str) -> bool:
        """
        Detect son-name questions.
        """

        son_terms = [
            "son",
            "son's name",
            "sons name",
            "my son's name",
            "my son name",
            "first born",
            "first-born",
        ]

        return any(term in text for term in son_terms)


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
        ARKA_SOURCE_AWARE_VALIDATOR_PHASE6C

        Require source/evidence context only for source-required routes.

        General knowledge, local profile, and math routes should not fail just
        because sources are empty. Explicit source/tool/status routes must have
        evidence before Arka claims a grounded result.
        """

        issues: List[ValidationIssue] = []

        requires_source = bool(context.get("requires_source", False))
        sources = context.get("sources", [])
        source_results = context.get("source_results", [])
        verified_actions = context.get("verified_actions", [])

        source_route = context.get("source_route", {}) or {}
        route = str(source_route.get("route", "") or "")
        source_type = source_route.get("source_type")
        allowed_without_source = bool(source_route.get("allowed_without_source", False))

        has_source_evidence = bool(sources or source_results)

        # ARKA_SOURCE_LIMITATION_PASS_PHASE6_FIX
        # A repaired limitation response should be allowed through.
        # Source-required routes should fail unsupported source claims, not honest
        # statements that explicitly refuse to claim source-backed results without evidence.
        source_limitation_markers = [
            "should not claim",
            "without verified",
            "needs to provide",
            "need source evidence",
            "need verified",
            "no verified source",
            "no verified",
            "source connector",
            "verified web results",
            "verified astraa/server/source evidence",
            "verified git/github command output",
            "verified server/status evidence",
            "verified payment/source evidence",
            "verified execution proof",
        ]

        lower_response = response.lower()
        is_source_limitation_response = any(
            marker in lower_response for marker in source_limitation_markers
        )

        if route == "ACTION_VERIFICATION_REQUIRED":
            has_source_evidence = has_source_evidence or bool(verified_actions)

        source_required_routes = {
            "WEB_SOURCE_REQUIRED": "MISSING_WEB_SOURCE",
            "ASTRAA_STATUS_REQUIRED": "MISSING_ASTRAA_STATUS_SOURCE",
            "GITHUB_REQUIRED": "MISSING_GITHUB_SOURCE",
            "SERVER_REQUIRED": "MISSING_SERVER_SOURCE",
            "PAYMENT_REQUIRED": "MISSING_PAYMENT_SOURCE",
            "ACTION_VERIFICATION_REQUIRED": "MISSING_ACTION_VERIFICATION",
        }

        if route in source_required_routes:
            if is_source_limitation_response:
                return issues

            if not has_source_evidence:
                issues.append(
                    ValidationIssue(
                        code=source_required_routes[route],
                        message=(
                            "Response requires source/evidence for route "
                            f"{route} but none was provided."
                        ),
                        severity="fail" if self.strict_mode else "warn",
                        field="source_route",
                    )
                )

            return issues

        if requires_source and not allowed_without_source and not has_source_evidence:
            issues.append(
                ValidationIssue(
                    code="MISSING_REQUIRED_SOURCE",
                    message=(
                        "Response requires a source but no source/evidence was provided."
                    ),
                    severity="fail" if self.strict_mode else "warn",
                    field="sources",
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
