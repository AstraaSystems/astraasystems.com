"""
response_policy.py

Phase 9A response policy module for Arka V1.

This module decides how Arka should present a final answer based on:
- prompt flags
- source route
- source execution state
- evidence availability
- action sensitivity
- profile/family context
- limitation state

It does not:
- execute tools
- call web/search/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state
- fabricate evidence
- change the actual facts in a response

Phase 9A is policy decision only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ResponseStyle(str, Enum):
    """
    User-facing answer style selected by response policy.
    """

    DIRECT_PROFILE = "DIRECT_PROFILE"
    FRIENDLY_PROFILE = "FRIENDLY_PROFILE"
    CONCISE_EVIDENCE = "CONCISE_EVIDENCE"
    DETAILED_EVIDENCE = "DETAILED_EVIDENCE"
    LIMITATION_ONLY = "LIMITATION_ONLY"
    GENERAL_KNOWLEDGE = "GENERAL_KNOWLEDGE"
    MATH_SUMMARY = "MATH_SUMMARY"
    ACTION_BLOCKED = "ACTION_BLOCKED"
    INTERNAL_TECHNICAL = "INTERNAL_TECHNICAL"
    DEFAULT = "DEFAULT"


@dataclass
class ResponsePolicyDecision:
    """
    Structured response policy decision.
    """

    style: ResponseStyle
    show_sources: bool = False
    show_limitations: bool = False
    show_internal_details: bool = False
    allow_evidence_formatting: bool = False
    allow_friendly_tone: bool = True
    preserve_original_response: bool = True
    reason: str = ""
    route: Optional[str] = None
    source_type: Optional[str] = None
    evidence_available: bool = False
    policy_warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "style": self.style.value,
            "show_sources": self.show_sources,
            "show_limitations": self.show_limitations,
            "show_internal_details": self.show_internal_details,
            "allow_evidence_formatting": self.allow_evidence_formatting,
            "allow_friendly_tone": self.allow_friendly_tone,
            "preserve_original_response": self.preserve_original_response,
            "reason": self.reason,
            "route": self.route,
            "source_type": self.source_type,
            "evidence_available": self.evidence_available,
            "policy_warnings": list(self.policy_warnings),
            "metadata": dict(self.metadata),
        }


class ResponsePolicy:
    """
    Decide final response style for Arka.

    Phase 9A does not format the response directly.
    It decides whether downstream formatting should be allowed.
    """

    SOURCE_REQUIRED_ROUTES = {
        "WEB_SOURCE_REQUIRED",
        "ASTRAA_STATUS_REQUIRED",
        "GITHUB_REQUIRED",
        "SERVER_REQUIRED",
        "PAYMENT_REQUIRED",
        "ACTION_VERIFICATION_REQUIRED",
    }

    EVIDENCE_STYLES = {
        "GITHUB_REQUIRED",
        "SERVER_REQUIRED",
        "ASTRAA_STATUS_REQUIRED",
        "PAYMENT_REQUIRED",
        "WEB_SOURCE_REQUIRED",
    }

    def decide(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResponsePolicyDecision:
        """
        Decide how a response should be presented.
        """

        context = context or {}
        prompt_flags = context.get("prompt_flags", {}) or {}
        source_route = context.get("source_route", {}) or {}
        source_execution = context.get("source_execution", {}) or {}

        route = str(source_route.get("route", "") or "")
        source_type = source_route.get("source_type")

        sources = context.get("sources", []) or []
        source_results = context.get("source_results", []) or []
        verified_actions = context.get("verified_actions", []) or []

        evidence_available = bool(sources or source_results or verified_actions)
        response_lower = (response or "").lower()

        # 1. Trusted local identity/profile/family answers.
        if self._is_profile_context(prompt_flags, route):
            return ResponsePolicyDecision(
                style=ResponseStyle.FRIENDLY_PROFILE,
                show_sources=False,
                show_limitations=False,
                show_internal_details=False,
                allow_evidence_formatting=False,
                allow_friendly_tone=True,
                preserve_original_response=True,
                reason="Prompt is answered from trusted local profile/family context.",
                route=route,
                source_type=source_type,
                evidence_available=evidence_available,
                metadata=self._metadata(source_route, source_execution),
            )

        # 2. Action-sensitive prompts without verified action evidence.
        if self._is_action_sensitive(prompt_flags, route) and not verified_actions:
            return ResponsePolicyDecision(
                style=ResponseStyle.ACTION_BLOCKED,
                show_sources=False,
                show_limitations=True,
                show_internal_details=False,
                allow_evidence_formatting=False,
                allow_friendly_tone=True,
                preserve_original_response=True,
                reason="Prompt is action-sensitive and lacks verified action evidence.",
                route=route,
                source_type=source_type,
                evidence_available=evidence_available,
                policy_warnings=["verified_action_required"],
                metadata=self._metadata(source_route, source_execution),
            )

        # 3. Source-required prompt with evidence.
        if route in self.EVIDENCE_STYLES and evidence_available:
            return ResponsePolicyDecision(
                style=ResponseStyle.CONCISE_EVIDENCE,
                show_sources=True,
                show_limitations=False,
                show_internal_details=False,
                allow_evidence_formatting=True,
                allow_friendly_tone=True,
                preserve_original_response=False,
                reason="Source evidence is available for a source-aware route.",
                route=route,
                source_type=source_type,
                evidence_available=evidence_available,
                metadata=self._metadata(source_route, source_execution),
            )

        # 4. Source-required prompt without evidence, but response is limitation wording.
        if route in self.SOURCE_REQUIRED_ROUTES and not evidence_available:
            if self._looks_like_limitation(response_lower):
                return ResponsePolicyDecision(
                    style=ResponseStyle.LIMITATION_ONLY,
                    show_sources=False,
                    show_limitations=True,
                    show_internal_details=False,
                    allow_evidence_formatting=False,
                    allow_friendly_tone=True,
                    preserve_original_response=True,
                    reason="Response is already honest limitation wording for missing evidence.",
                    route=route,
                    source_type=source_type,
                    evidence_available=False,
                    metadata=self._metadata(source_route, source_execution),
                )

            return ResponsePolicyDecision(
                style=ResponseStyle.LIMITATION_ONLY,
                show_sources=False,
                show_limitations=True,
                show_internal_details=False,
                allow_evidence_formatting=False,
                allow_friendly_tone=True,
                preserve_original_response=True,
                reason="Source-required route lacks evidence; answer should not claim sourced facts.",
                route=route,
                source_type=source_type,
                evidence_available=False,
                policy_warnings=["missing_source_evidence"],
                metadata=self._metadata(source_route, source_execution),
            )

        # 5. Math prompts.
        if route == "MATH_REQUIRED" or bool(prompt_flags.get("is_math_question", False)):
            return ResponsePolicyDecision(
                style=ResponseStyle.MATH_SUMMARY,
                show_sources=False,
                show_limitations=False,
                show_internal_details=False,
                allow_evidence_formatting=False,
                allow_friendly_tone=True,
                preserve_original_response=True,
                reason="Prompt is math/calculation-oriented.",
                route=route,
                source_type=source_type,
                evidence_available=evidence_available,
                metadata=self._metadata(source_route, source_execution),
            )

        # 6. General knowledge prompts.
        if route == "GENERAL_KNOWLEDGE":
            return ResponsePolicyDecision(
                style=ResponseStyle.GENERAL_KNOWLEDGE,
                show_sources=False,
                show_limitations=False,
                show_internal_details=False,
                allow_evidence_formatting=False,
                allow_friendly_tone=True,
                preserve_original_response=True,
                reason="Prompt is general knowledge and does not require source evidence.",
                route=route,
                source_type=source_type,
                evidence_available=evidence_available,
                metadata=self._metadata(source_route, source_execution),
            )

        # 7. Internal technical prompts about Arka itself.
        if bool(prompt_flags.get("is_arka_question", False)):
            return ResponsePolicyDecision(
                style=ResponseStyle.INTERNAL_TECHNICAL,
                show_sources=False,
                show_limitations=False,
                show_internal_details=False,
                allow_evidence_formatting=False,
                allow_friendly_tone=True,
                preserve_original_response=True,
                reason="Prompt appears to be about Arka/internal technical context.",
                route=route,
                source_type=source_type,
                evidence_available=evidence_available,
                metadata=self._metadata(source_route, source_execution),
            )

        # Default.
        return ResponsePolicyDecision(
            style=ResponseStyle.DEFAULT,
            show_sources=False,
            show_limitations=False,
            show_internal_details=False,
            allow_evidence_formatting=False,
            allow_friendly_tone=True,
            preserve_original_response=True,
            reason="No specific response policy matched; using default style.",
            route=route,
            source_type=source_type,
            evidence_available=evidence_available,
            metadata=self._metadata(source_route, source_execution),
        )

    def _is_profile_context(
        self,
        prompt_flags: Dict[str, Any],
        route: str,
    ) -> bool:
        return (
            route == "LOCAL_PROFILE"
            or bool(prompt_flags.get("is_identity_question", False))
            or bool(prompt_flags.get("is_family_identity_question", False))
        )

    def _is_action_sensitive(
        self,
        prompt_flags: Dict[str, Any],
        route: str,
    ) -> bool:
        return (
            route == "ACTION_VERIFICATION_REQUIRED"
            or bool(prompt_flags.get("is_action_claim_sensitive", False))
        )

    def _looks_like_limitation(self, response_lower: str) -> bool:
        markers = [
            "should not claim",
            "without verified",
            "need verified",
            "needs to provide",
            "no verified",
            "source evidence",
            "execution proof",
            "cannot confirm",
        ]

        return any(marker in response_lower for marker in markers)

    def _metadata(
        self,
        source_route: Dict[str, Any],
        source_execution: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "policy_version": "phase9",
            "policy": "arka_v1.core.response_policy",
            "external_calls": False,
            "memory_mutation": False,
            "tool_execution": False,
            "source_route": dict(source_route),
            "source_execution_status": source_execution.get("status"),
            "source_execution_executed": source_execution.get("executed"),
        }


def decide_response_policy(
    prompt: str,
    response: str,
    context: Optional[Dict[str, Any]] = None,
) -> ResponsePolicyDecision:
    """
    Convenience function for response policy decision.
    """

    policy = ResponsePolicy()
    return policy.decide(prompt=prompt, response=response, context=context)
