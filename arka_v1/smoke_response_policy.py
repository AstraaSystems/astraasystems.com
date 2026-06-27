"""
smoke_response_policy.py

Phase 9B smoke proof for Arka response policy.

This test proves response_policy.py selects the correct final-answer policy
for profile, evidence, limitation, general knowledge, math, and action-sensitive prompts.

It does not mutate memory or runtime state.
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path
from types import ModuleType


ARKA_DIR = Path(__file__).resolve().parent

PROFILE_LOADER = ARKA_DIR / "core" / "profile_loader.py"
SOURCE_ROUTER = ARKA_DIR / "core" / "source_router.py"
CONTEXT_BUILDER = ARKA_DIR / "core" / "context_builder.py"
SOURCE_EXECUTION_BRIDGE = ARKA_DIR / "core" / "source_execution_bridge.py"
RESPONSE_POLICY = ARKA_DIR / "core" / "response_policy.py"


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


def _compile_modules() -> None:
    for path in [
        PROFILE_LOADER,
        SOURCE_ROUTER,
        CONTEXT_BUILDER,
        SOURCE_EXECUTION_BRIDGE,
        RESPONSE_POLICY,
    ]:
        py_compile.compile(str(path), doraise=True)

    print("[OK] Compile passed for Phase 9 response policy dependencies")


def _load_dependencies():
    profile_loader = _load_module("profile_loader_phase9_smoke", PROFILE_LOADER)
    sys.modules["core.profile_loader"] = profile_loader

    source_router = _load_module("source_router_phase9_smoke", SOURCE_ROUTER)
    sys.modules["core.source_router"] = source_router

    context_builder = _load_module("context_builder_phase9_smoke", CONTEXT_BUILDER)
    sys.modules["core.context_builder"] = context_builder

    source_execution_bridge = _load_module(
        "source_execution_bridge_phase9_smoke",
        SOURCE_EXECUTION_BRIDGE,
    )
    sys.modules["core.source_execution_bridge"] = source_execution_bridge

    response_policy = _load_module("response_policy_phase9_smoke", RESPONSE_POLICY)
    sys.modules["core.response_policy"] = response_policy

    print("[OK] Loaded Phase 9 smoke dependencies directly by file path")

    return context_builder, source_execution_bridge, response_policy


def _context_for(prompt: str, context_builder: ModuleType, source_execution_bridge: ModuleType):
    context = context_builder.build_context(prompt)
    execution = source_execution_bridge.execute_source_route(prompt, context)
    return source_execution_bridge.merge_source_execution(context, execution)


def _check(
    prompt: str,
    response: str,
    expected_style: str,
    expected_show_sources: bool,
    expected_formatting: bool,
    context_builder: ModuleType,
    source_execution_bridge: ModuleType,
    response_policy: ModuleType,
) -> None:
    context = _context_for(prompt, context_builder, source_execution_bridge)

    decision = response_policy.decide_response_policy(
        prompt=prompt,
        response=response,
        context=context,
    )

    actual_style = getattr(decision.style, "value", decision.style)

    print("")
    print("PROMPT:", prompt)
    print("route:", context["source_route"]["route"])
    print("style:", actual_style)
    print("show_sources:", decision.show_sources)
    print("allow_evidence_formatting:", decision.allow_evidence_formatting)
    print("reason:", decision.reason)

    assert actual_style == expected_style, decision
    assert decision.show_sources is expected_show_sources, decision
    assert decision.allow_evidence_formatting is expected_formatting, decision


def main() -> int:
    _compile_modules()

    context_builder, source_execution_bridge, response_policy = _load_dependencies()

    cases = [
        (
            "who am I?",
            "You are Keshanth Sivayogampillai.",
            "FRIENDLY_PROFILE",
            False,
            False,
        ),
        (
            "what is my son's name?",
            "Your first-born son's name is Bhirav Aditya.",
            "FRIENDLY_PROFILE",
            False,
            False,
        ),
        (
            "show git status",
            "Generic Git status response.",
            "CONCISE_EVIDENCE",
            True,
            True,
        ),
        (
            "what branch am I on?",
            "Generic branch response.",
            "CONCISE_EVIDENCE",
            True,
            True,
        ),
        (
            "how to cook rice",
            "Rinse rice, add water, simmer, and rest.",
            "GENERAL_KNOWLEDGE",
            False,
            False,
        ),
        (
            "calculate income from DoorDash",
            "Estimated income is calculated.",
            "MATH_SUMMARY",
            False,
            False,
        ),
        (
            "do a web search about how to cook rice",
            "I should not claim a web-sourced answer without verified web results.",
            "LIMITATION_ONLY",
            False,
            False,
        ),
        (
            "git push origin main",
            "I should not claim that action was completed without verified execution proof.",
            "ACTION_BLOCKED",
            False,
            False,
        ),
    ]

    for prompt, response, style, show_sources, formatting in cases:
        _check(
            prompt,
            response,
            style,
            show_sources,
            formatting,
            context_builder,
            source_execution_bridge,
            response_policy,
        )

    print("")
    print("[OK] Phase 9 response policy smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
