"""
smoke_capability_limitation_formatter.py

Phase 14B smoke proof for capability_limitation_formatter.py.

This test proves capability-aware limitation messages are formatted for:
- disabled web source capability
- disabled Astraa status capability
- disabled server health capability
- disabled payment status capability
- unsafe Git action block

It also proves successful Git evidence is not limitation-formatted.

It does not:
- execute destructive tools
- mutate memory
- write runtime state
- fabricate external results
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
    "capability_limitation_formatter": ARKA_DIR / "core" / "capability_limitation_formatter.py",
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
    print("[OK] Compile passed for Phase 14 capability limitation formatter dependencies")


def load_all():
    profile_loader = load_module("profile_loader_phase14", FILES["profile_loader"])
    sys.modules["core.profile_loader"] = profile_loader

    source_router = load_module("source_router_phase14", FILES["source_router"])
    sys.modules["core.source_router"] = source_router

    capability_registry = load_module(
        "capability_registry_phase14",
        FILES["capability_registry"],
    )
    sys.modules["core.capability_registry"] = capability_registry

    context_builder = load_module("context_builder_phase14", FILES["context_builder"])
    sys.modules["core.context_builder"] = context_builder

    source_execution_bridge = load_module(
        "source_execution_bridge_phase14",
        FILES["source_execution_bridge"],
    )
    sys.modules["core.source_execution_bridge"] = source_execution_bridge

    formatter = load_module(
        "capability_limitation_formatter_phase14",
        FILES["capability_limitation_formatter"],
    )
    sys.modules["core.capability_limitation_formatter"] = formatter

    print("[OK] Loaded Phase 14 dependencies directly by file path")

    return context_builder, source_execution_bridge, formatter


def build_merged_context(prompt, context_builder, source_execution_bridge):
    context = context_builder.build_context(prompt)
    execution = source_execution_bridge.execute_source_route(prompt, context)
    merged = source_execution_bridge.merge_source_execution(context, execution)
    return context, execution, merged


def check_limited(
    prompt,
    expected_route,
    expected_blocked_reason,
    expected_text,
    context_builder,
    source_execution_bridge,
    formatter,
):
    context, execution, merged = build_merged_context(
        prompt,
        context_builder,
        source_execution_bridge,
    )

    result = formatter.format_capability_limitation(
        prompt=prompt,
        response="Original limitation.",
        context=merged,
    )

    print("")
    print("PROMPT:", prompt)
    print("route:", context["source_route"]["route"])
    print("blocked_reason:", execution.get("blocked_reason"))
    print("formatted:", result.formatted)
    print("response:", result.response)

    assert context["source_route"]["route"] == expected_route, context
    assert execution.get("blocked_reason") == expected_blocked_reason, execution
    assert result.formatted is True, result
    assert expected_text in result.response, result.response
    assert result.metadata["tool_execution"] is False, result
    assert result.metadata["memory_mutation"] is False, result
    assert result.metadata["runtime_writes"] is False, result
    assert result.metadata["fabricated_results"] is False, result


def check_no_limitation(
    prompt,
    context_builder,
    source_execution_bridge,
    formatter,
):
    context, execution, merged = build_merged_context(
        prompt,
        context_builder,
        source_execution_bridge,
    )

    result = formatter.format_capability_limitation(
        prompt=prompt,
        response="Original Git status answer.",
        context=merged,
    )

    print("")
    print("PROMPT:", prompt)
    print("route:", context["source_route"]["route"])
    print("status:", execution.get("status"))
    print("blocked_reason:", execution.get("blocked_reason"))
    print("formatted:", result.formatted)

    assert execution["status"] == "success", execution
    assert execution.get("blocked_reason") is None, execution
    assert result.formatted is False, result
    assert result.response == "Original Git status answer.", result


def main():
    compile_all()

    context_builder, source_execution_bridge, formatter = load_all()

    check_limited(
        "do a web search about how to cook rice",
        "WEB_SOURCE_REQUIRED",
        "capability_disabled",
        "web source capability is registered",
        context_builder,
        source_execution_bridge,
        formatter,
    )

    check_limited(
        "check astraasystems.com website status",
        "ASTRAA_STATUS_REQUIRED",
        "capability_disabled",
        "Astraa status capability is registered",
        context_builder,
        source_execution_bridge,
        formatter,
    )

    check_limited(
        "is the backend server healthy?",
        "SERVER_REQUIRED",
        "capability_disabled",
        "server health capability is registered",
        context_builder,
        source_execution_bridge,
        formatter,
    )

    check_limited(
        "check Moneris payment status",
        "PAYMENT_REQUIRED",
        "capability_disabled",
        "payment status capability is registered",
        context_builder,
        source_execution_bridge,
        formatter,
    )

    check_limited(
        "git push origin main",
        "GITHUB_REQUIRED",
        "unsafe_git_action_blocked",
        "No Git action was performed",
        context_builder,
        source_execution_bridge,
        formatter,
    )

    check_no_limitation(
        "show git status",
        context_builder,
        source_execution_bridge,
        formatter,
    )

    print("")
    print("[OK] Phase 14 capability limitation formatter smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
