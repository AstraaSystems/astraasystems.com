"""
context_builder.py

Phase 3 trusted context builder for Arka V1.

This module builds structured runtime context for each Arka response.

It does not:
- answer prompts
- dispatch tools
- call web/search/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state

It only creates trusted context for validator, repairer, and future dispatch layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PromptFlags:
    """
    Lightweight prompt classification flags.

    These flags are not final intent routing.
    They only provide safe context hints for validation/repair.
    """

    is_identity_question: bool = False
    is_source_question: bool = False
    is_action_claim_sensitive: bool = False
    is_math_question: bool = False
    is_website_status_question: bool = False
    is_github_question: bool = False
    is_family_identity_question: bool = False
    is_astraa_question: bool = False
    is_arka_question: bool = False


@dataclass
class ArkaContext:
    """
    Structured trusted context object for Arka V1.
    """

    owner_name: str
    system_name: str = "Arka V1"
    mode: str = "local"
    authority: str = "owner"

    requires_source: bool = False
    sources: List[str] = field(default_factory=list)
    verified_actions: List[str] = field(default_factory=list)

    prompt_flags: PromptFlags = field(default_factory=PromptFlags)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context object into plain dictionary for existing validator/repairer APIs.
        """

        return {
            "owner_name": self.owner_name,
            "system_name": self.system_name,
            "mode": self.mode,
            "authority": self.authority,
            "requires_source": self.requires_source,
            "sources": list(self.sources),
            "verified_actions": list(self.verified_actions),
            "prompt_flags": {
                "is_identity_question": self.prompt_flags.is_identity_question,
                "is_source_question": self.prompt_flags.is_source_question,
                "is_action_claim_sensitive": self.prompt_flags.is_action_claim_sensitive,
                "is_math_question": self.prompt_flags.is_math_question,
                "is_website_status_question": self.prompt_flags.is_website_status_question,
                "is_github_question": self.prompt_flags.is_github_question,
                "is_family_identity_question": self.prompt_flags.is_family_identity_question,
                "is_astraa_question": self.prompt_flags.is_astraa_question,
                "is_arka_question": self.prompt_flags.is_arka_question,
            },
            "metadata": dict(self.metadata),
        }


class ContextBuilder:
    """
    Builds trusted runtime context for Arka.

    Phase 3 keeps this deliberately conservative:
    - safe defaults
    - local owner/system identity
    - prompt classification hints
    - no external calls
    """

    def __init__(
        self,
        owner_name: str = "Keshanth Sivayogampillai",
        system_name: str = "Arka V1",
        mode: str = "local",
        authority: str = "owner",
    ) -> None:
        self.owner_name = owner_name
        self.system_name = system_name
        self.mode = mode
        self.authority = authority

    def build(self, prompt: str) -> Dict[str, Any]:
        """
        Build trusted context for a single raw user prompt.
        """

        normalized = self._normalize(prompt)

        flags = PromptFlags(
            is_identity_question=self._is_identity_question(normalized),
            is_source_question=self._is_source_question(normalized),
            is_action_claim_sensitive=self._is_action_claim_sensitive(normalized),
            is_math_question=self._is_math_question(normalized),
            is_website_status_question=self._is_website_status_question(normalized),
            is_github_question=self._is_github_question(normalized),
            is_family_identity_question=self._is_family_identity_question(normalized),
            is_astraa_question=self._is_astraa_question(normalized),
            is_arka_question=self._is_arka_question(normalized),
        )

        requires_source = self._requires_source(flags)

        context = ArkaContext(
            owner_name=self.owner_name,
            system_name=self.system_name,
            mode=self.mode,
            authority=self.authority,
            requires_source=requires_source,
            sources=[],
            verified_actions=[],
            prompt_flags=flags,
            metadata={
                "context_version": "phase3",
                "builder": "arka_v1.core.context_builder",
                "external_calls": False,
                "memory_mutation": False,
            },
        )

        return context.to_dict()

    def _normalize(self, prompt: str) -> str:
        """
        Normalize prompt for conservative keyword matching.
        """

        return (prompt or "").strip().lower()

    def _is_identity_question(self, text: str) -> bool:
        """
        Detect owner identity questions.
        """

        return text in {
            "who am i",
            "who am i?",
            "whoami",
            "what is my name",
            "what is my name?",
            "identify me",
            "identify me?",
            "who is the owner",
            "who owns arka",
            "who is arka built for",
            "who is keshanth",
            "who is keshanth?",
        }

    def _is_family_identity_question(self, text: str) -> bool:
        """
        Detect family-memory identity questions.

        These should prefer trusted local memory/context, not web search.
        """

        family_terms = [
            "my son",
            "son's name",
            "sons name",
            "my son's name",
            "my wife",
            "wife's name",
            "wifes name",
            "my wife's name",
            "first born",
            "first-born",
        ]

        return any(term in text for term in family_terms)

    def _is_source_question(self, text: str) -> bool:
        """
        Detect prompts that likely require verified sources.

        This does not fetch sources. It only marks that sources are required.
        """

        source_terms = [
            "search",
            "web",
            "latest",
            "current",
            "today",
            "price",
            "prices",
            "flight",
            "github",
            "netlify",
            "server",
            "website status",
            "health",
            "has anyone signed up",
            "signup",
            "sign up",
            "signed up",
            "moneris",
            "payment",
            "deployment",
            "deployed",
            "live",
            "status",
        ]

        return any(term in text for term in source_terms)

    def _is_action_claim_sensitive(self, text: str) -> bool:
        """
        Detect prompts involving actions where Arka must not falsely claim completion.
        """

        action_terms = [
            "send",
            "sent",
            "delete",
            "deleted",
            "deploy",
            "deployed",
            "push",
            "pushed",
            "commit",
            "committed",
            "purchase",
            "purchased",
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

        return any(term in text for term in action_terms)

    def _is_math_question(self, text: str) -> bool:
        """
        Detect prompts that should likely use Math OS or calculation logic.
        """

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

    def _is_website_status_question(self, text: str) -> bool:
        """
        Detect Astraa website/server health/status prompts.
        """

        website_terms = [
            "website",
            "astraasystems.com",
            "health",
            "status",
            "server",
            "api",
            "endpoint",
            "netlify",
            "frontend",
            "backend",
        ]

        return any(term in text for term in website_terms)

    def _is_github_question(self, text: str) -> bool:
        """
        Detect Git/GitHub workflow prompts.
        """

        github_terms = [
            "github",
            "git",
            "commit",
            "branch",
            "tag",
            "push",
            "pull",
            "pull request",
            "repo",
            "repository",
            "remote",
            "origin",
            "merge",
            "fetch",
            "clone",
        ]

        return any(term in text for term in github_terms)

    def _is_astraa_question(self, text: str) -> bool:
        """
        Detect Astraa ecosystem prompts.
        """

        astraa_terms = [
            "astraa",
            "astraasystems.com",
            "estimator",
            "finance tool",
            "operations tool",
            "workspace",
            "moneris",
            "netlify",
            "lead",
            "signup",
            "signed up",
        ]

        return any(term in text for term in astraa_terms)

    def _is_arka_question(self, text: str) -> bool:
        """
        Detect Arka/Ardhanarishvara ecosystem prompts.
        """

        arka_terms = [
            "arka",
            "aruhan",
            "ardhanarishvara",
            "math os",
            "governor",
            "response validator",
            "response repairer",
            "context builder",
            "hq",
        ]

        return any(term in text for term in arka_terms)

    def _requires_source(self, flags: PromptFlags) -> bool:
        """
        Decide source requirement from flags.

        Identity and family identity should not require external source by default.
        Source, GitHub, website, payment, deployment, and live-status prompts should.
        """

        if flags.is_identity_question or flags.is_family_identity_question:
            return False

        return any(
            [
                flags.is_source_question,
                flags.is_website_status_question,
                flags.is_github_question,
            ]
        )


def build_context(prompt: str) -> Dict[str, Any]:
    """
    Convenience function for simple pipeline integration.
    """

    builder = ContextBuilder()
    return builder.build(prompt)
