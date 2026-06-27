"""
smoke_capability_execution_integration.py

Phase 12 smoke proof for capability-aware source execution.

This test proves source_execution_bridge.py now respects capability_registry.py:
- enabled read-only Git capability executes
- disabled web/Astraa/server/payment placeholders do not execute
- unsafe Git action prompt is blocked
- general/math/profile no-op routes remain not_required

It does not mutate memory or runtime state.
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
    print("[OK] Compile passed for Phase 12 capability execution dependencies")


def load_all():
    profile_loader = load_module("profile_loader_phase12", FILES["profile_loader"])
    sys.modules["core.profile_loader"] = profile_loader

    source_router = load_module("source_router_phase12", FILES["source_router"])
    sys.modules["core.source_router"] = source_router

    capability_registry = load_module(
        "capability_registry_phase12",
        FILES["capability_registry"],
    )
    sys.modules["core.capability_registry"] = capability_registry

    context_builder = load_module("context_builder_phase12", FILES["context_builder"])
    sys.modules["core.context_builder"] = context_builder

    source_execution_bridge = load_module(
        "source_execution_bridge_phase12",
        FILES["source_execution_bridge"],
    )
    sys.modules["core.source_execution_bridge"] = source_execution_bridge

    print("[OK] Loaded Phase 12 dependencies directly by file path")

    return context_builder, capability_registry, source_execution_bridge


def check_case(
    prompt,
    expected_route,
    expected_capability,
    expected_capability_enabled,
    expected_executed,
    expected_status,
    expected_blocked_reason,
    context_builder,
    capability_registry,
    source_execution_bridge,
):
    context = context_builder.build_context(prompt)
    route = context["source_route"]["route"]

    capability = capability_registry.decide_capability_for_context(context).to_dict()
    result = source_execution_bridge.execute_source_route(prompt, context)

    print("")
    print("PROMPT:", prompt)
    print("route:", route)
    print("capability:", capability.get("capability_name"))
    print("capability_enabled:", capability.get("enabled"))
    print("executed:", result["executed"])
    print("status:", result["status"])
    print("blocked_reason:", result.get("blocked_reason"))

    assert route == expected_route, context
    assert capability["capability_name"] == expected_capability, capability
    assert capability["enabled"] is expected_capability_enabled, capability
    assert capability["mutates_state"] is False, capability
    assert capability["metadata"]["tool_execution"] is False, capability

    assert result["executed"] is expected_executed, result
    assert result["status"] == expected_status, result

    if expected_blocked_reason is not None:
        assert result.get("blocked_reason") == expected_blocked_reason, result

    if expected_executed:
        assert "local_git" in result.get("sources", []), result
        assert len(result.get("source_results", [])) >= 1, result


def check_noop(prompt, expected_route, context_builder, source_execution_bridge):
    context = context_builder.build_context(prompt)
    result = source_execution_bridge.execute_source_route(prompt, context)

    print("")
    print("PROMPT:", prompt)
    print("route:", context["source_route"]["route"])
    print("executed:", result["executed"])
    print("status:", result["status"])

    assert context["source_route"]["route"] == expected_route, context
    assert result["executed"] is False, result
    assert result["status"] == "not_required", result


def main():
    compile_all()

    context_builder, capability_registry, source_execution_bridge = load_all()

    check_case(
        "show git status",
        "GITHUB_REQUIRED",
        "local_git_readonly",
        True,
        True,
        "success",
        None,
        context_builder,
        capability_registry,
        source_execution_bridge,
    )

    check_case(
        "do a web search about how to cook rice",
        "WEB_SOURCE_REQUIRED",
        "web_source_placeholder",
        False,
        False,
        "not_implemented",
        "capability_disabled",
        context_builder,
        capability_registry,
        source_execution_bridge,
    )

    check_case(
        "check astraasystems.com website status",
        "ASTRAA_STATUS_REQUIRED",
        "astraa_status_placeholder",
        False,
        False,
        "not_implemented",
        "capability_disabled",
        context_builder,
        capability_registry,
        source_execution_bridge,
    )

    check_case(
        "is the backend server healthy?",
        "SERVER_REQUIRED",
        "server_health_placeholder",
        False,
        False,
        "not_implemented",
        "capability_disabled",
        context_builder,
        capability_registry,
        source_execution_bridge,
    )

    check_case(
        "check Moneris payment status",
        "PAYMENT_REQUIRED",
        "payment_status_placeholder",
        False,
        False,
        "not_implemented",
        "capability_disabled",
        context_builder,
        capability_registry,
        source_execution_bridge,
    )

    # Git push still routes as GITHUB_REQUIRED, but the read-only Git executor
    # must block it as an unsafe action prompt.
    check_case(
        "git push origin main",
        "GITHUB_REQUIRED",
        "local_git_readonly",
        True,
        False,
        "blocked",
        "unsafe_git_action_blocked",
        context_builder,
        capability_registry,
        source_execution_bridge,
    )

    check_noop(
        "how to cook rice",
        "GENERAL_KNOWLEDGE",
        context_builder,
        source_execution_bridge,
    )

    check_noop(
        "calculate income from DoorDash",
        "MATH_REQUIRED",
        context_builder,
        source_execution_bridge,
    )

    check_noop(
        "who am I?",
        "LOCAL_PROFILE",
        context_builder,
        source_execution_bridge,
    )

    print("")
    print("[OK] Phase 12 capability-aware execution integration smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
