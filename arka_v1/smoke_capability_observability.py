"""
smoke_capability_observability.py

Phase 13B smoke proof for capability-aware policy observability.

This test proves policy_observer.py safely reports capability metadata:
- capability_name
- capability_enabled
- capability_read_only
- capability_requires_approval
- capability_mutates_state
- capability_blocked_reason

It does not:
- execute destructive tools
- mutate memory
- write runtime state
- log raw prompt/response/source content/profile values
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ARKA_DIR = Path(__file__).resolve().parent

FILES = {
    "profile_loader": ARKA_DIR / "core" / "profile_loader.py",
    "source_router": ARKA_DIR / "core" / "source_router.py",
    "context_builder": ARKA_DIR / "core" / "context_builder.py",
    "capability_registry": ARKA_DIR / "core" / "capability_registry.py",
    "source_execution_bridge": ARKA_DIR / "core" / "source_execution_bridge.py",
    "response_policy": ARKA_DIR / "core" / "response_policy.py",
    "policy_observer": ARKA_DIR / "core" / "policy_observer.py",
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def compile_all():
    for path in FILES.values():
        py_compile.compile(str(path), doraise=True)
    print("[OK] Compile passed for Phase 13 capability observability dependencies")


def load_all():
    profile_loader = load_module("profile_loader_phase13", FILES["profile_loader"])
    sys.modules["core.profile_loader"] = profile_loader

    source_router = load_module("source_router_phase13", FILES["source_router"])
    sys.modules["core.source_router"] = source_router

    capability_registry = load_module(
        "capability_registry_phase13",
        FILES["capability_registry"],
    )
    sys.modules["core.capability_registry"] = capability_registry

    context_builder = load_module("context_builder_phase13", FILES["context_builder"])
    sys.modules["core.context_builder"] = context_builder

    source_execution_bridge = load_module(
        "source_execution_bridge_phase13",
        FILES["source_execution_bridge"],
    )
    sys.modules["core.source_execution_bridge"] = source_execution_bridge

    response_policy = load_module("response_policy_phase13", FILES["response_policy"])
    sys.modules["core.response_policy"] = response_policy

    policy_observer = load_module("policy_observer_phase13", FILES["policy_observer"])
    sys.modules["core.policy_observer"] = policy_observer

    print("[OK] Loaded Phase 13 dependencies directly by file path")

    return context_builder, source_execution_bridge, response_policy, policy_observer


def observe_case(prompt, response, context_builder, source_execution_bridge, response_policy, policy_observer):
    context = context_builder.build_context(prompt)
    execution = source_execution_bridge.execute_source_route(prompt, context)
    merged = source_execution_bridge.merge_source_execution(context, execution)

    decision = response_policy.decide_response_policy(
        prompt=prompt,
        response=response,
        context=merged,
    )

    observation = policy_observer.observe_response_policy(
        prompt=prompt,
        response=response,
        context=merged,
        policy_decision=decision,
        formatter_result=None,
        validation_result=None,
        enabled=False,
    )

    return context, execution, observation.to_dict()


def check_case(
    prompt,
    response,
    expected_route,
    expected_capability_name,
    expected_enabled,
    expected_read_only,
    expected_requires_approval,
    expected_mutates_state,
    expected_blocked_reason,
    context_builder,
    source_execution_bridge,
    response_policy,
    policy_observer,
):
    context, execution, event = observe_case(
        prompt,
        response,
        context_builder,
        source_execution_bridge,
        response_policy,
        policy_observer,
    )

    print("")
    print("PROMPT:", prompt)
    print("route:", event["route"])
    print("capability_name:", event["capability_name"])
    print("capability_enabled:", event["capability_enabled"])
    print("capability_read_only:", event["capability_read_only"])
    print("capability_requires_approval:", event["capability_requires_approval"])
    print("capability_mutates_state:", event["capability_mutates_state"])
    print("capability_blocked_reason:", event["capability_blocked_reason"])

    assert event["route"] == expected_route, event
    assert event["capability_name"] == expected_capability_name, event
    assert event["capability_enabled"] is expected_enabled, event
    assert event["capability_read_only"] is expected_read_only, event
    assert event["capability_requires_approval"] is expected_requires_approval, event
    assert event["capability_mutates_state"] is expected_mutates_state, event
    assert event["capability_blocked_reason"] == expected_blocked_reason, event

    metadata = event["metadata"]
    assert metadata["raw_prompt_logged"] is False, event
    assert metadata["raw_response_logged"] is False, event
    assert metadata["source_content_logged"] is False, event
    assert metadata["profile_values_logged"] is False, event
    assert metadata["sensitive_fields_omitted"] is True, event
    assert metadata["persisted"] is False, event
    assert metadata["memory_mutation"] is False, event
    assert metadata["tool_execution"] is False, event


def main():
    compile_all()

    (
        context_builder,
        source_execution_bridge,
        response_policy,
        policy_observer,
    ) = load_all()

    check_case(
        "show git status",
        "Generic Git status response.",
        "GITHUB_REQUIRED",
        "local_git_readonly",
        True,
        True,
        False,
        False,
        None,
        context_builder,
        source_execution_bridge,
        response_policy,
        policy_observer,
    )

    check_case(
        "do a web search about how to cook rice",
        "I should not claim a web-sourced answer without verified web results.",
        "WEB_SOURCE_REQUIRED",
        "web_source_placeholder",
        False,
        True,
        False,
        False,
        "capability_disabled",
        context_builder,
        source_execution_bridge,
        response_policy,
        policy_observer,
    )

    check_case(
        "check astraasystems.com website status",
        "I should not claim Astraa website status without verified evidence.",
        "ASTRAA_STATUS_REQUIRED",
        "astraa_status_placeholder",
        False,
        True,
        False,
        False,
        "capability_disabled",
        context_builder,
        source_execution_bridge,
        response_policy,
        policy_observer,
    )

    check_case(
        "git push origin main",
        "I should not claim that action was completed without verified execution proof.",
        "GITHUB_REQUIRED",
        "local_git_readonly",
        True,
        True,
        False,
        False,
        "unsafe_git_action_blocked",
        context_builder,
        source_execution_bridge,
        response_policy,
        policy_observer,
    )

    print("")
    print("[OK] Phase 13 capability observability smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
