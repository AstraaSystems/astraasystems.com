"""
smoke_evidence_response_formatter.py

Phase 8B smoke proof for Arka evidence response formatter.

This test proves that Phase 7 source execution evidence can be formatted by
Phase 8 evidence_response_formatter.py.

It does not mutate memory or runtime state.
It only uses read-only Git evidence already supported by source_execution_bridge.
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path
from types import ModuleType


ARKA_DIR = Path(__file__).resolve().parent
ROOT = ARKA_DIR.parent

CONTEXT_BUILDER = ARKA_DIR / "core" / "context_builder.py"
SOURCE_ROUTER = ARKA_DIR / "core" / "source_router.py"
PROFILE_LOADER = ARKA_DIR / "core" / "profile_loader.py"
SOURCE_EXECUTION_BRIDGE = ARKA_DIR / "core" / "source_execution_bridge.py"
EVIDENCE_FORMATTER = ARKA_DIR / "core" / "evidence_response_formatter.py"


def _load_module_from_path(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module spec for {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


def _compile_modules() -> None:
    py_compile.compile(str(CONTEXT_BUILDER), doraise=True)
    py_compile.compile(str(SOURCE_ROUTER), doraise=True)
    py_compile.compile(str(PROFILE_LOADER), doraise=True)
    py_compile.compile(str(SOURCE_EXECUTION_BRIDGE), doraise=True)
    py_compile.compile(str(EVIDENCE_FORMATTER), doraise=True)

    print("[OK] Compile passed for Phase 8 evidence formatter dependencies")


def _load_dependencies():
    profile_loader = _load_module_from_path(
        "profile_loader_phase8_smoke_module",
        PROFILE_LOADER,
    )
    sys.modules["core.profile_loader"] = profile_loader

    source_router = _load_module_from_path(
        "source_router_phase8_smoke_module",
        SOURCE_ROUTER,
    )
    sys.modules["core.source_router"] = source_router

    context_builder = _load_module_from_path(
        "context_builder_phase8_smoke_module",
        CONTEXT_BUILDER,
    )
    sys.modules["core.context_builder"] = context_builder

    source_execution_bridge = _load_module_from_path(
        "source_execution_bridge_phase8_smoke_module",
        SOURCE_EXECUTION_BRIDGE,
    )
    sys.modules["core.source_execution_bridge"] = source_execution_bridge

    evidence_formatter = _load_module_from_path(
        "evidence_formatter_phase8_smoke_module",
        EVIDENCE_FORMATTER,
    )
    sys.modules["core.evidence_response_formatter"] = evidence_formatter

    print("[OK] Loaded Phase 8 smoke dependencies directly by file path")

    return context_builder, source_execution_bridge, evidence_formatter


def _format_from_prompt(
    prompt: str,
    context_builder: ModuleType,
    source_execution_bridge: ModuleType,
    evidence_formatter: ModuleType,
):
    context = context_builder.build_context(prompt)
    execution = source_execution_bridge.execute_source_route(prompt, context)
    merged = source_execution_bridge.merge_source_execution(context, execution)

    result = evidence_formatter.format_response_with_evidence(
        prompt=prompt,
        response="Generic response before formatting.",
        context=merged,
    )

    return context, execution, merged, result


def _test_git_status_formatting(
    context_builder: ModuleType,
    source_execution_bridge: ModuleType,
    evidence_formatter: ModuleType,
) -> None:
    context, execution, merged, result = _format_from_prompt(
        "show git status",
        context_builder,
        source_execution_bridge,
        evidence_formatter,
    )

    assert context["source_route"]["route"] == "GITHUB_REQUIRED", context
    assert execution["executed"] is True, execution
    assert "local_git" in merged.get("sources", []), merged
    assert len(merged.get("source_results", [])) >= 1, merged

    assert result.formatted is True, result
    assert result.used_evidence is True, result
    assert "Source: local_git" in result.response, result.response

    print("[OK] Phase 8 formats Git status evidence")


def _test_git_branch_formatting(
    context_builder: ModuleType,
    source_execution_bridge: ModuleType,
    evidence_formatter: ModuleType,
) -> None:
    context, execution, merged, result = _format_from_prompt(
        "what branch am I on?",
        context_builder,
        source_execution_bridge,
        evidence_formatter,
    )

    assert context["source_route"]["route"] == "GITHUB_REQUIRED", context
    assert execution["executed"] is True, execution
    assert "local_git" in merged.get("sources", []), merged

    assert result.formatted is True, result
    assert "Current branch:" in result.response, result.response
    assert "Source: local_git" in result.response, result.response

    print("[OK] Phase 8 formats current Git branch evidence")


def _test_git_log_formatting(
    context_builder: ModuleType,
    source_execution_bridge: ModuleType,
    evidence_formatter: ModuleType,
) -> None:
    context, execution, merged, result = _format_from_prompt(
        "show recent commits",
        context_builder,
        source_execution_bridge,
        evidence_formatter,
    )

    assert context["source_route"]["route"] == "GITHUB_REQUIRED", context
    assert execution["executed"] is True, execution
    assert "local_git" in merged.get("sources", []), merged

    assert result.formatted is True, result
    assert "Recent commits:" in result.response, result.response
    assert "Source: local_git" in result.response, result.response

    print("[OK] Phase 8 formats recent Git commit evidence")


def _test_git_remote_formatting(
    context_builder: ModuleType,
    source_execution_bridge: ModuleType,
    evidence_formatter: ModuleType,
) -> None:
    context, execution, merged, result = _format_from_prompt(
        "what remote is configured?",
        context_builder,
        source_execution_bridge,
        evidence_formatter,
    )

    assert context["source_route"]["route"] == "GITHUB_REQUIRED", context
    assert execution["executed"] is True, execution
    assert "local_git" in merged.get("sources", []), merged

    assert result.formatted is True, result
    assert "Configured Git remotes:" in result.response, result.response
    assert "Source: local_git" in result.response, result.response

    print("[OK] Phase 8 formats Git remote evidence")


def _test_no_evidence_keeps_response(evidence_formatter: ModuleType) -> None:
    result = evidence_formatter.format_response_with_evidence(
        prompt="hello",
        response="Hello back.",
        context={},
    )

    assert result.formatted is False, result
    assert result.used_evidence is False, result
    assert result.response == "Hello back.", result

    print("[OK] Phase 8 leaves responses unchanged when no evidence exists")


def main() -> int:
    _compile_modules()

    context_builder, source_execution_bridge, evidence_formatter = _load_dependencies()

    _test_git_status_formatting(
        context_builder,
        source_execution_bridge,
        evidence_formatter,
    )
    _test_git_branch_formatting(
        context_builder,
        source_execution_bridge,
        evidence_formatter,
    )
    _test_git_log_formatting(
        context_builder,
        source_execution_bridge,
        evidence_formatter,
    )
    _test_git_remote_formatting(
        context_builder,
        source_execution_bridge,
        evidence_formatter,
    )
    _test_no_evidence_keeps_response(evidence_formatter)

    print("")
    print("[OK] Phase 8 Git evidence formatting proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
