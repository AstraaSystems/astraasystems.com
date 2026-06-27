"""
source_router.py

Phase 6 source-aware routing module for Arka V1.

This module classifies what kind of source, tool, or route a prompt needs.

It does not:
- answer prompts
- execute web searches
- execute Git/GitHub commands
- call Astraa, Netlify, Moneris, server, or payment systems
- mutate memory
- write runtime state

It only returns a structured route decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SourceRoute(str, Enum):
    """
    Primary source/tool route for a prompt.
    """

    LOCAL_PROFILE = "LOCAL_PROFILE"
    GENERAL_KNOWLEDGE = "GENERAL_KNOWLEDGE"
    WEB_SOURCE_REQUIRED = "WEB_SOURCE_REQUIRED"
    ASTRAA_STATUS_REQUIRED = "ASTRAA_STATUS_REQUIRED"
    GITHUB_REQUIRED = "GITHUB_REQUIRED"
    SERVER_REQUIRED = "SERVER_REQUIRED"
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    ACTION_VERIFICATION_REQUIRED = "ACTION_VERIFICATION_REQUIRED"
    MATH_REQUIRED = "MATH_REQUIRED"
    UNKNOWN = "UNKNOWN"


@dataclass
class SourceRouteDecision:
    """
    Structured source routing decision.
    """

    route: SourceRoute
    requires_source: bool
    source_type: Optional[str] = None
    allowed_without_source: bool = False
    reason: str = ""
    confidence: str = "medium"
    secondary_routes: List[SourceRoute] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert route decision into a plain dictionary for context_builder.
        """

        return {
            "route": self.route.value,
            "requires_source": self.requires_source,
            "source_type": self.source_type,
            "allowed_without_source": self.allowed_without_source,
            "reason": self.reason,
            "confidence": self.confidence,
            "secondary_routes": [route.value for route in self.secondary_routes],
            "required_capabilities": list(self.required_capabilities),
            "metadata": dict(self.metadata),
        }


class SourceRouter:
    """
    Classifies prompts into source/tool routing categories.

    Phase 6A is classification only. It deliberately does not execute tools.
    """

    def route(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SourceRouteDecision:
        """
        Classify a prompt into a source route decision.
        """

        context = context or {}
        text = self._normalize(prompt)
        prompt_flags = context.get("prompt_flags", {})

        # Highest priority: local profile identity/family facts.
        if self._is_local_profile_prompt(text, prompt_flags):
            return SourceRouteDecision(
                route=SourceRoute.LOCAL_PROFILE,
                requires_source=False,
                source_type="profile",
                allowed_without_source=True,
                reason="Prompt asks for trusted local owner/family profile context.",
                confidence="high",
                required_capabilities=["profile_context"],
                metadata=self._metadata(),
            )

        # ARKA_OPERATIONAL_ROUTE_PRIORITY_PHASE7D
        # Specific operational/status routes must win before broad Git/web routing.
        # Example: "check astraasystems.com website status" should route to
        # ASTRAA_STATUS_REQUIRED, not GITHUB_REQUIRED.

        # Astraa / website / signup / app status checks.
        if self._is_astraa_status_prompt(text):
            return SourceRouteDecision(
                route=SourceRoute.ASTRAA_STATUS_REQUIRED,
                requires_source=True,
                source_type="astraa_status",
                allowed_without_source=False,
                reason="Prompt requires Astraa website/app/status/source evidence.",
                confidence="high",
                required_capabilities=["astraa_status_source"],
                secondary_routes=self._secondary_action_routes(text),
                metadata=self._metadata(),
            )

        # Server/API/backend/frontend/Netlify status.
        if self._is_server_prompt(text):
            return SourceRouteDecision(
                route=SourceRoute.SERVER_REQUIRED,
                requires_source=True,
                source_type="server_status",
                allowed_without_source=False,
                reason="Prompt requires server/API/frontend/backend/Netlify status evidence.",
                confidence="high",
                required_capabilities=["server_status_source"],
                secondary_routes=self._secondary_action_routes(text),
                metadata=self._metadata(),
            )

        # Payment/Moneris prompts.
        if self._is_payment_prompt(text):
            return SourceRouteDecision(
                route=SourceRoute.PAYMENT_REQUIRED,
                requires_source=True,
                source_type="payment_status",
                allowed_without_source=False,
                reason="Prompt requires payment/Moneris/source evidence.",
                confidence="high",
                required_capabilities=["payment_source"],
                secondary_routes=self._secondary_action_routes(text),
                metadata=self._metadata(),
            )

        # Read-only Git prompts like "show current branch" contain words such as
        # "current", but should route to Git evidence, not web search.
        if self._is_github_prompt(text):
            secondary = self._secondary_action_routes(text)

            return SourceRouteDecision(
                route=SourceRoute.GITHUB_REQUIRED,
                requires_source=True,
                source_type="github_or_git",
                allowed_without_source=False,
                reason="Prompt requires Git/GitHub/local repository evidence or command output.",
                confidence="high",
                required_capabilities=["git_or_github_source"],
                secondary_routes=secondary,
                metadata=self._metadata(),
            )

        # Explicit web/source request must not be treated as generic knowledge.
        if self._explicit_web_source_request(text):
            return SourceRouteDecision(
                route=SourceRoute.WEB_SOURCE_REQUIRED,
                requires_source=True,
                source_type="web",
                allowed_without_source=False,
                reason="Prompt explicitly requests web/search/latest/current source-backed information.",
                confidence="high",
                required_capabilities=["web_source"],
                metadata=self._metadata(),
            )

        # Action verification prompts: did you push/deploy/send/delete/etc.
        if self._is_action_verification_prompt(text):
            return SourceRouteDecision(
                route=SourceRoute.ACTION_VERIFICATION_REQUIRED,
                requires_source=True,
                source_type="action_verification",
                allowed_without_source=False,
                reason="Prompt involves an action claim that requires execution proof before confirmation.",
                confidence="high",
                required_capabilities=["verified_action_evidence"],
                metadata=self._metadata(),
            )

        # Math/calculation prompts should route to Math OS later, but Phase 6A only classifies.
        if self._is_math_prompt(text, prompt_flags):
            return SourceRouteDecision(
                route=SourceRoute.MATH_REQUIRED,
                requires_source=False,
                source_type="math",
                allowed_without_source=True,
                reason="Prompt appears to require calculation or Math OS routing, not external source evidence by default.",
                confidence="medium",
                required_capabilities=["math"],
                metadata=self._metadata(),
            )

        # General knowledge: answerable without live source unless user explicitly requested live/source-backed info.
        if self._is_general_knowledge_prompt(text):
            return SourceRouteDecision(
                route=SourceRoute.GENERAL_KNOWLEDGE,
                requires_source=False,
                source_type=None,
                allowed_without_source=True,
                reason="Prompt appears to ask general knowledge without explicit live/source requirement.",
                confidence="medium",
                required_capabilities=["general_reasoning"],
                metadata=self._metadata(),
            )

        return SourceRouteDecision(
            route=SourceRoute.UNKNOWN,
            requires_source=False,
            source_type=None,
            allowed_without_source=True,
            reason="No specific source route matched; defaulting to unknown/general handling.",
            confidence="low",
            required_capabilities=[],
            metadata=self._metadata(),
        )

    def _normalize(self, prompt: str) -> str:
        return (prompt or "").strip().lower()

    def _metadata(self) -> Dict[str, Any]:
        return {
            "router_version": "phase6",
            "router": "arka_v1.core.source_router",
            "external_calls": False,
            "memory_mutation": False,
            "tool_execution": False,
        }

    def _is_local_profile_prompt(
        self,
        text: str,
        prompt_flags: Dict[str, Any],
    ) -> bool:
        if bool(prompt_flags.get("is_identity_question", False)):
            return True

        if bool(prompt_flags.get("is_family_identity_question", False)):
            return True

        local_terms = [
            "who am i",
            "who am i?",
            "whoami",
            "what is my name",
            "what is my name?",
            "identify me",
            "who is the owner",
            "who owns arka",
            "who is arka built for",
            "what is my son's name",
            "what is my son name",
            "what's my son's name",
            "what is my wife's name",
            "what is my wife name",
            "what's my wife's name",
        ]

        return any(term in text for term in local_terms)

    def _explicit_web_source_request(self, text: str) -> bool:
        explicit_terms = [
            "web search",
            "search web",
            "search the web",
            "do a web search",
            "look online",
            "latest",
            "current",
            "live",
            "today",
            "news",
            "price today",
            "prices today",
            "flight price",
            "flight prices",
            "current price",
            "current prices",
        ]

        return any(term in text for term in explicit_terms)

    def _is_astraa_status_prompt(self, text: str) -> bool:
        astraa_terms = [
            "astraasystems.com",
            "astraa website",
            "astraa status",
            "website status",
            "has anyone signed up",
            "signed up for estimator",
            "estimator signup",
            "lead capture",
            "astraa lead",
            "astraa bridge",
        ]

        return any(term in text for term in astraa_terms)

    def _is_github_prompt(self, text: str) -> bool:
        """
        ARKA_GIT_READONLY_ROUTING_PHASE7B

        Detect Git/GitHub prompts, including read-only repository evidence
        requests such as branch/status/log/remote checks.
        """

        github_terms = [
            "github",
            "git",
            "git status",
            "git log",
            "git push",
            "git pull",
            "git fetch",
            "git branch",
            "git remote",
            "commit",
            "commits",
            "branch",
            "current branch",
            "what branch",
            "show branch",
            "show current branch",
            "status",
            "repo status",
            "repository status",
            "recent commits",
            "latest commits",
            "show recent commits",
            "show git log",
            "tag",
            "repo",
            "repository",
            "origin/main",
            "origin remote",
            "what is origin",
            "show remotes",
            "remote",
            "pull request",
        ]

        return any(term in text for term in github_terms)

    def _is_server_prompt(self, text: str) -> bool:
        server_terms = [
            "server",
            "backend",
            "frontend",
            "api",
            "endpoint",
            "netlify",
            "deployment",
            "deployed",
            "health check",
            "health endpoint",
            "status endpoint",
        ]

        return any(term in text for term in server_terms)

    def _is_payment_prompt(self, text: str) -> bool:
        payment_terms = [
            "payment",
            "moneris",
            "receipt",
            "transaction",
            "checkout",
            "invoice",
            "paid",
            "billing",
        ]

        return any(term in text for term in payment_terms)

    def _is_action_verification_prompt(self, text: str) -> bool:
        action_terms = [
            "did you",
            "have you",
            "was it",
            "is it done",
            "confirm",
            "verify",
            "pushed",
            "deployed",
            "deleted",
            "sent",
            "submitted",
            "installed",
            "created",
            "moved",
            "renamed",
        ]

        sensitive_action_terms = [
            "push",
            "pushed",
            "deploy",
            "deployed",
            "delete",
            "deleted",
            "send",
            "sent",
            "submit",
            "submitted",
            "install",
            "installed",
            "create",
            "created",
            "move",
            "moved",
            "rename",
            "renamed",
        ]

        return any(term in text for term in action_terms) and any(
            term in text for term in sensitive_action_terms
        )

    def _secondary_action_routes(self, text: str) -> List[SourceRoute]:
        if self._is_action_verification_prompt(text):
            return [SourceRoute.ACTION_VERIFICATION_REQUIRED]

        action_command_terms = [
            "push",
            "deploy",
            "delete",
            "send",
            "submit",
            "install",
            "create",
            "move",
            "rename",
        ]

        if any(term in text for term in action_command_terms):
            return [SourceRoute.ACTION_VERIFICATION_REQUIRED]

        return []

    def _is_math_prompt(
        self,
        text: str,
        prompt_flags: Dict[str, Any],
    ) -> bool:
        if bool(prompt_flags.get("is_math_question", False)):
            return True

        math_terms = [
            "calculate",
            "calculation",
            "math",
            "sum",
            "average",
            "percent",
            "percentage",
            "%",
            "profit",
            "income",
            "cost",
            "estimate",
            "revenue",
            "margin",
            "ratio",
            "total",
            "difference",
            "multiply",
            "divide",
        ]

        return any(term in text for term in math_terms)

    def _is_general_knowledge_prompt(self, text: str) -> bool:
        general_terms = [
            "how do i",
            "how to",
            "explain",
            "what is",
            "why",
            "help me understand",
            "give me an overview",
            "summarize",
        ]

        return any(term in text for term in general_terms)


def route_source(
    prompt: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function for source route classification.
    """

    router = SourceRouter()
    return router.route(prompt=prompt, context=context).to_dict()
