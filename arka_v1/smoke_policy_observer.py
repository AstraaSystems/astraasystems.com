"""
smoke_policy_observer.py

Phase 10B smoke proof for Arka policy observer.

This test proves policy_observer.py returns safe compact observations for:
- profile/family prompts
- Git evidence prompts
- missing-source limitation prompts
- action-blocked prompts

It does not:
- execute destructive tools
- mutate memory
- write runtime state
- log raw prompts/responses/source content/profile values
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
POLICY_OBSERVER = ARKA_DIR / "core" / "policy_observer.py"


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
        POLICY_OBSERVER,
    ]:
        py_compile.compile(str(path), doraise=True)

    print("[OK] Compile passed for Phase 10 policy observer dependencies")


def _load_dependencies():
    profile_loader = _load_module("profile_loader_phase10_smoke", PROFILE_LOADER)
    sys.modules["core.profile_loader"] = profile_loader

    source_router = _load_module("source_router_phase10_smoke", SOURCE_ROUTER)
    sys.modules["core.source_router"] = source_router

    context_builder = _load_module("context_builder_phase10_smoke", CONTEXT_BUILDER)
    sys.modules["core.context_builder"] = context_builder

    source_execution_bridge = _load_module(
        "source_execution_bridge_phase10_smoke",
        SOURCE_EXECUTION_BRIDGE,
    )
    sys.modules["core.source_execution_bridge"] = source_execution_bridge

    response_policy = _load_module("response_policy_phase10_smoke", RESPONSE_POLICY)
    sys.modules["core.response_policy"] = response_policy

    policy_observer = _load_module("policy_observer_phase10_smoke", POLICY_OBSERVER)
    sys.modules["core.policy_observer"] = policy_observer

    print("[OK] Loaded Phase 10 smoke dependencies directly by file path")

    return context_builder, source_execution_bridge, response_policy, policy_observer


def _context_for(prompt: str, context_builder: ModuleType, source_execution_bridge: ModuleType):
    context = context_builder.build_context(prompt)
    execution = source_execution_bridge.execute_source_route(prompt, context)
    return source_execution_bridge.merge_source_execution(context, execution)


def _observe(
    *,
    prompt: str,
    response: str,
    context_builder: ModuleType,
    source_execution_bridge: ModuleType,
    response_policy: ModuleType,
    policy_observer: ModuleType,
):
    context = _context_for(prompt, context_builder, source_execution_bridge)

    decision = response_policy.decide_response_policy(
        prompt=prompt,
        response=response,
        context=context,
    )

    observation = policy_observer.observe_response_policy(
        prompt=prompt,
        response=response,
        context=context,
        policy_decision=decision,
        formatter_result=None,
        validation_result=None,
        enabled=False,
    )

    return context, decision, observation, observation.to_dict()


def _assert_safe_metadata(event: dict) -> None:
    metadata = event["metadata"]

    assert metadata["raw_prompt_logged"] is False, event
    assert metadata["raw_response_logged"] is False, event
    assert metadata["source_content_logged"] is False, event
    assert metadata["profile_values_logged"] is False, event
    assert metadata["sensitive_fields_omitted"] is True, event
    assert metadata["persisted"] is False, event
    assert metadata["memory_mutation"] is False, event
    assert metadata["tool_execution"] is False, event
    assert "observer_not_persisting_enabled_false" in event["warnings"], event


def _check(
    *,
    prompt: str,
    response: str,
    expected_route: str,
    expected_style: str,
    expected_evidence_available: bool,
    expected_action_blocked: bool,
    expected_limitation_selected: bool,
    context_builder: ModuleType,
    source_execution_bridge: ModuleType,
    response_policy: ModuleType,
    policy_observer: ModuleType,
) -> None:
    context, decision, observation, event = _observe(
        prompt=prompt,
        response=response,
        context_builder=context_builder,
        source_execution_bridge=source_execution_bridge,
        response_policy=response_policy,
        policy_observer=policy_observer,
    )

    print("")
    print("PROMPT:", prompt)
    print("route:", event["route"])
    print("style:", event["style"])
    print("evidence_available:", event["evidence_available"])
    print("action_blocked:", event["action_blocked"])
    print("limitation_selected:", event["limitation_selected"])
    print("source_execution_status:", event["source_execution_status"])
    print("warnings:", event["warnings"])

    assert event["event_type"] == "response_policy_observation", event
    assert event["observed"] is True, event
    assert event["route"] == expected_route, event
    assert event["style"] == expected_style, event
    assert event["evidence_available"] is expected_evidence_available, event
    assert event["action_blocked"] is expected_action_blocked, event
    assert event["limitation_selected"] is expected_limitation_selected, event

    _assert_safe_metadata(event)


def main() -> int:
    _compile_modules()

    (
        context_builder,
        source_execution_bridge,
        response_policy,
        policy_observer,
    ) = _load_dependencies()

    cases = [
        {
            "prompt": "who am I?",
            "response": "You are Keshanth Sivayogampillai.",
            "expected_route": "LOCAL_PROFILE",
            "expected_style": "FRIENDLY_PROFILE",
            "expected_evidence_available": False,
            "expected_action_blocked": False,
            "expected_limitation_selected": False,
        },
        {
            "prompt": "show git status",
            "response": "Generic Git status response.",
            "expected_route": "GITHUB_REQUIRED",
            "expected_style": "CONCISE_EVIDENCE",
            "expected_evidence_available": True,
            "expected_action_blocked": False,
            "expected_limitation_selected": False,
        },
        {
            "prompt": "do a web search about how to cook rice",
            "response": "I should not claim a web-sourced answer without verified web results.",
            "expected_route": "WEB_SOURCE_REQUIRED",
            "expected_style": "LIMITATION_ONLY",
            "expected_evidence_available": False,
            "expected_action_blocked": False,
            "expected_limitation_selected": True,
        },
        {
            "prompt": "git push origin main",
            "response": "I should not claim that action was completed without verified execution proof.",
            "expected_route": "GITHUB_REQUIRED",
            "expected_style": "ACTION_BLOCKED",
            "expected_evidence_available": False,
            "expected_action_blocked": True,
            "expected_limitation_selected": False,
        },
    ]

    for case in cases:
        _check(
            **case,
            context_builder=context_builder,
            source_execution_bridge=source_execution_bridge,
            response_policy=response_policy,
            policy_observer=policy_observer,
        )

    print("")
    print("[OK] Phase 10 policy observer smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
