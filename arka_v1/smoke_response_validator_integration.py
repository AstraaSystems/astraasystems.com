#!/usr/bin/env python3
"""
smoke_response_validator_integration.py

Smoke test for Arka Phase 1 response validator integration.

This test verifies:
1. response_validator.py compiles
2. arka_v1.py compiles
3. direct validator PASS behavior
4. direct validator FAIL behavior
5. integrated arka_reply() repairs a bad identity response
6. integrated arka_reply() allows a good identity response

Important:
The repo currently contains both:
- arka_v1/ directory
- arka_v1/arka_v1.py file

That means normal package imports can be shadowed by the arka_v1.py module.
To avoid false failures, this smoke test loads the validator directly from file
and registers a core.response_validator alias for the integrated runtime path.
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
import types
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
ARKA_DIR = ROOT / "arka_v1"
ARKA_APP = ARKA_DIR / "arka_v1.py"
VALIDATOR = ARKA_DIR / "core" / "response_validator.py"
CONTEXT_BUILDER = ARKA_DIR / "core" / "context_builder.py"
PROFILE_LOADER = ARKA_DIR / "core" / "profile_loader.py"
SOURCE_ROUTER = ARKA_DIR / "core" / "source_router.py"
SOURCE_EXECUTION_BRIDGE = ARKA_DIR / "core" / "source_execution_bridge.py"
ARKA_STATE = ARKA_DIR / "arka_state.json"


def _add_paths() -> None:
    """
    Ensure Arka local modules can be imported from repo root or arka_v1 folder.
    """

    for path in (ROOT, ARKA_DIR):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


def _compile_targets() -> None:
    """
    Compile critical files before running behavioral tests.
    """

    py_compile.compile(str(VALIDATOR), doraise=True)
    py_compile.compile(str(CONTEXT_BUILDER), doraise=True)
    py_compile.compile(str(PROFILE_LOADER), doraise=True)
    py_compile.compile(str(SOURCE_ROUTER), doraise=True)
    py_compile.compile(str(SOURCE_EXECUTION_BRIDGE), doraise=True)
    py_compile.compile(str(ARKA_APP), doraise=True)

    print("[OK] Compile passed for response_validator.py and arka_v1.py")


def _load_module_from_path(module_name: str, path: Path) -> ModuleType:
    """
    Load a Python module directly from a file path.
    """

    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not create import spec for {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def _load_validator_module() -> ModuleType:
    """
    Load response_validator.py directly and register import aliases.

    The integrated arka_v1.py code tries:
    1. from arka_v1.core.response_validator import ...
    2. from core.response_validator import ...

    Because arka_v1.py can shadow the arka_v1 package during this smoke test,
    we make sure core.response_validator is available.
    """

    validator_module = _load_module_from_path(
        "response_validator_smoke_module",
        VALIDATOR,
    )

    core_pkg = types.ModuleType("core")
    core_pkg.__path__ = [str(ARKA_DIR / "core")]

    sys.modules["core"] = core_pkg
    sys.modules["core.response_validator"] = validator_module

    print("[OK] Loaded response_validator.py directly and registered core alias")

    return validator_module


def _load_profile_loader_module() -> ModuleType:
    """
    Load profile_loader.py directly and register core.profile_loader alias.
    """

    profile_loader_module = _load_module_from_path(
        "profile_loader_smoke_module",
        PROFILE_LOADER,
    )

    sys.modules["core.profile_loader"] = profile_loader_module

    print("[OK] Loaded profile_loader.py directly and registered core alias")

    return profile_loader_module


def _load_source_router_module() -> ModuleType:
    """
    Load source_router.py directly and register core.source_router alias.
    """

    source_router_module = _load_module_from_path(
        "source_router_smoke_module",
        SOURCE_ROUTER,
    )

    sys.modules["core.source_router"] = source_router_module

    print("[OK] Loaded source_router.py directly and registered core alias")

    return source_router_module


def _load_source_execution_bridge_module() -> ModuleType:
    """
    Load source_execution_bridge.py directly and register core.source_execution_bridge alias.
    """

    source_execution_bridge_module = _load_module_from_path(
        "source_execution_bridge_smoke_module",
        SOURCE_EXECUTION_BRIDGE,
    )

    sys.modules["core.source_execution_bridge"] = source_execution_bridge_module

    print("[OK] Loaded source_execution_bridge.py directly and registered core alias")

    return source_execution_bridge_module


def _load_context_builder_module() -> ModuleType:
    """
    Load context_builder.py directly and register core.context_builder alias.
    """

    context_builder_module = _load_module_from_path(
        "context_builder_smoke_module",
        CONTEXT_BUILDER,
    )

    sys.modules["core.context_builder"] = context_builder_module

    print("[OK] Loaded context_builder.py directly and registered core alias")

    return context_builder_module


def _load_arka_runtime() -> ModuleType:
    """
    Load arka_v1.py as an isolated runtime module.

    We avoid normal package import because the repo has both:
    - arka_v1/ directory
    - arka_v1/arka_v1.py file
    """

    runtime = _load_module_from_path("arka_runtime_smoke_module", ARKA_APP)

    if not hasattr(runtime, "arka_reply"):
        raise RuntimeError("arka_v1.py does not expose arka_reply(raw)")

    if not hasattr(runtime, "arka_governor_dispatch"):
        raise RuntimeError("arka_v1.py does not expose arka_governor_dispatch")

    print("[OK] Loaded arka_v1.py runtime module")

    return runtime


def _test_phase7_source_execution_bridge(
    context_builder_module: ModuleType,
    source_execution_bridge_module: ModuleType,
) -> None:
    """
    Direct Phase 7 source execution bridge test.

    Proves read-only Git prompts collect local_git evidence and unsafe Git
    action prompts remain blocked.
    """

    cases = [
        ("show git status", True, "success", "GITHUB_REQUIRED"),
        ("what branch am I on?", True, "success", "GITHUB_REQUIRED"),
        ("show recent commits", True, "success", "GITHUB_REQUIRED"),
        ("what remote is configured?", True, "success", "GITHUB_REQUIRED"),
        ("git push origin main", False, "blocked", "GITHUB_REQUIRED"),
        ("how to cook rice", False, "not_required", "GENERAL_KNOWLEDGE"),
    ]

    for prompt, expected_executed, expected_status, expected_route in cases:
        context = context_builder_module.build_context(prompt)
        result = source_execution_bridge_module.execute_source_route(prompt, context)
        merged = source_execution_bridge_module.merge_source_execution(context, result)

        assert context["source_route"]["route"] == expected_route, context
        assert result["executed"] is expected_executed, result
        assert result["status"] == expected_status, result

        if expected_executed:
            assert "local_git" in merged.get("sources", []), merged
            assert len(merged.get("source_results", [])) >= 1, merged

        if expected_status == "blocked":
            assert result.get("blocked_reason") == "unsafe_git_action_blocked", result

    print("[OK] Direct Phase 7 source execution bridge works")


def _test_phase6_source_routes(context_builder_module: ModuleType) -> None:
    """
    Direct Phase 6 source-aware routing test through build_context().
    """

    cases = [
        ("how to cook rice", "GENERAL_KNOWLEDGE", False),
        ("do a web search about how to cook rice", "WEB_SOURCE_REQUIRED", True),
        ("check astraasystems.com website status", "ASTRAA_STATUS_REQUIRED", True),
        ("git push origin main", "GITHUB_REQUIRED", True),
        ("calculate income from DoorDash", "MATH_REQUIRED", False),
    ]

    for prompt, expected_route, expected_requires_source in cases:
        context = context_builder_module.build_context(prompt)
        source_route = context.get("source_route", {})

        assert context["metadata"].get("context_version") == "phase6", context
        assert source_route.get("route") == expected_route, source_route
        assert context.get("requires_source") is expected_requires_source, context

    print("[OK] Direct Phase 6 source-aware routing works")


def _test_profile_backed_context(context_builder_module: ModuleType) -> None:
    """
    Direct Phase 4 profile-backed context test.
    """

    context = context_builder_module.build_context("what is my son's name?")

    assert context["metadata"].get("context_version") == "phase6", context
    assert context["metadata"].get("profile_version") == "phase4", context
    assert context["metadata"].get("profile_loaded") is True, context

    family = context.get("family", {})

    assert family.get("wife_name") == "Thrilochana", family
    assert family.get("first_born_son_name") == "Bhirav Aditya", family
    assert context["requires_source"] is False, context
    assert context["prompt_flags"]["is_family_identity_question"] is True, context

    print("[OK] Direct Phase 4 profile-backed context works")


def _test_direct_validator_pass(validator_module: ModuleType) -> None:
    """
    Direct validator PASS test.
    """

    result = validator_module.validate_response(
        prompt="who am I?",
        response="You are Keshanth Sivayogampillai.",
        context={
            "owner_name": "Keshanth Sivayogampillai",
            "requires_source": False,
            "sources": [],
        },
        strict_mode=True,
    )

    assert result.status == validator_module.ValidationStatus.PASS, result
    assert result.ok is True, result
    assert result.issues == [], result.issues

    print("[OK] Direct validator PASS case works")


def _test_direct_validator_fail(validator_module: ModuleType) -> None:
    """
    Direct validator FAIL test.
    """

    result = validator_module.validate_response(
        prompt="who am I?",
        response="I could not pull reliable live snippets.",
        context={
            "owner_name": "Keshanth Sivayogampillai",
        },
        strict_mode=True,
    )

    issue_codes = [issue.code for issue in result.issues]

    assert result.status == validator_module.ValidationStatus.FAIL, result
    assert result.ok is False, result
    assert "OWNER_IDENTITY_CONFUSION" in issue_codes, issue_codes

    print("[OK] Direct validator FAIL case works")


def _test_integrated_pipeline_repairs_bad_identity(runtime: ModuleType) -> None:
    """
    Integrated pipeline test.

    Monkeypatch governor dispatch to return a bad identity response.
    arka_reply() should pass it through Phase 1 validation, repair it through
    Phase 2, validate the repaired response, and return the repaired answer.
    """

    def fake_bad_dispatch(raw: str, web_func=None) -> str:
        return "I could not pull reliable live snippets."

    runtime.arka_governor_dispatch = fake_bad_dispatch

    response = runtime.arka_reply("who am I?")

    assert isinstance(response, str), type(response)
    assert "You are Keshanth Sivayogampillai" in response, response
    assert "Phase 1 validation" not in response, response
    assert "OWNER_IDENTITY_CONFUSION" not in response, response

    print("[OK] Integrated pipeline repairs bad identity response")


def _test_integrated_pipeline_repairs_bad_son_identity(runtime: ModuleType) -> None:
    """
    Integrated Phase 5 test.

    Monkeypatch governor dispatch to return a bad son's-name response.
    arka_reply() should validate, repair using profile-backed family context,
    revalidate, and return the repaired son's-name answer.
    """

    def fake_bad_dispatch(raw: str, web_func=None) -> str:
        return "I could not pull reliable live snippets."

    runtime.arka_governor_dispatch = fake_bad_dispatch

    response = runtime.arka_reply("what is my son's name?")

    assert isinstance(response, str), type(response)
    assert "Bhirav Aditya" in response, response
    assert "Phase 1 validation" not in response, response
    assert "FAMILY_IDENTITY_CONFUSION" not in response, response

    print("[OK] Integrated pipeline repairs bad son identity response")


def _test_integrated_pipeline_repairs_bad_wife_identity(runtime: ModuleType) -> None:
    """
    Integrated Phase 5 test.

    Monkeypatch governor dispatch to return a bad wife's-name response.
    arka_reply() should validate, repair using profile-backed family context,
    revalidate, and return the repaired wife's-name answer.
    """

    def fake_bad_dispatch(raw: str, web_func=None) -> str:
        return "I could not pull reliable live snippets."

    runtime.arka_governor_dispatch = fake_bad_dispatch

    response = runtime.arka_reply("what is my wife's name?")

    assert isinstance(response, str), type(response)
    assert "Thrilochana" in response, response
    assert "Phase 1 validation" not in response, response
    assert "FAMILY_IDENTITY_CONFUSION" not in response, response

    print("[OK] Integrated pipeline repairs bad wife identity response")


def _test_integrated_pipeline_repairs_missing_web_source(runtime: ModuleType) -> None:
    """
    Integrated Phase 6 test.

    If governor claims web results without source evidence, arka_reply()
    should return source-aware limitation wording instead of fake web evidence.
    """

    def fake_bad_dispatch(raw: str, web_func=None) -> str:
        return "Here are web search results about cooking rice."

    runtime.arka_governor_dispatch = fake_bad_dispatch

    response = runtime.arka_reply("do a web search about how to cook rice")

    assert isinstance(response, str), type(response)
    assert "web-sourced answer" in response, response
    assert "verified web results" in response, response
    assert "Here are web search results" not in response, response

    print("[OK] Integrated pipeline repairs missing web source response")


def _test_integrated_pipeline_repairs_missing_astraa_status_source(runtime: ModuleType) -> None:
    """
    Integrated Phase 6 test.

    If governor claims Astraa status without source evidence, arka_reply()
    should return source-aware limitation wording.
    """

    def fake_bad_dispatch(raw: str, web_func=None) -> str:
        return "The Astraa website is live."

    runtime.arka_governor_dispatch = fake_bad_dispatch

    response = runtime.arka_reply("check astraasystems.com website status")

    assert isinstance(response, str), type(response)
    assert "Astraa website" in response, response
    assert "verified Astraa/server/source evidence" in response, response
    assert response != "The Astraa website is live.", response

    print("[OK] Integrated pipeline repairs missing Astraa status source response")


def _test_integrated_pipeline_uses_git_source_execution(runtime: ModuleType) -> None:
    """
    Integrated Phase 7 test.

    Because Phase 7C executes read-only Git evidence before validation, a Git
    evidence prompt should not fail with MISSING_GITHUB_SOURCE when local_git
    evidence is available in context.
    """

    def fake_git_status_response(raw: str, web_func=None) -> str:
        return "Git status evidence is available from local Git."

    runtime.arka_governor_dispatch = fake_git_status_response

    response = runtime.arka_reply("show git status")

    assert isinstance(response, str), type(response)

    # Phase 8 evidence formatter should replace the generic governor response
    # with formatted local_git evidence.
    assert "Source: local_git" in response, response
    assert (
        "You are on branch" in response
        or "Git status evidence was captured" in response
        or "Git working tree changes shown" in response
    ), response

    assert "MISSING_GITHUB_SOURCE" not in response, response
    assert "I should not claim Git or GitHub" not in response, response
    assert "Phase 1 validation" not in response, response

    print("[OK] Integrated pipeline formats read-only Git source execution evidence")


def _test_integrated_pipeline_repairs_missing_github_source(runtime: ModuleType) -> None:
    """
    Integrated Phase 6 test.

    If governor claims Git/GitHub action results without evidence, arka_reply()
    should return source-aware limitation wording.
    """

    def fake_bad_dispatch(raw: str, web_func=None) -> str:
        return "I pushed the branch."

    runtime.arka_governor_dispatch = fake_bad_dispatch

    response = runtime.arka_reply("git push origin main")

    assert isinstance(response, str), type(response)
    assert "Git or GitHub" in response, response
    assert "verified Git/GitHub command output" in response, response
    assert response != "I pushed the branch.", response

    print("[OK] Integrated pipeline repairs missing GitHub source response")


def _test_integrated_pipeline_allows_good_identity(runtime: ModuleType) -> None:
    """
    Integrated pipeline test.

    Monkeypatch governor dispatch to return the correct identity response.
    arka_reply() should allow it through.
    """

    def fake_good_dispatch(raw: str, web_func=None) -> str:
        return "You are Keshanth Sivayogampillai."

    runtime.arka_governor_dispatch = fake_good_dispatch

    response = runtime.arka_reply("who am I?")

    assert isinstance(response, str), type(response)
    assert "You are Keshanth Sivayogampillai" in response, response
    assert "Phase 1 validation" not in response, response
    assert "OWNER_IDENTITY_CONFUSION" not in response, response

    print("[OK] Integrated pipeline allows good identity response")


def _snapshot_runtime_state() -> bytes | None:
    """
    Snapshot arka_state.json as raw bytes so smoke tests do not leave runtime
    log changes or line-ending/encoding changes.
    """

    if not ARKA_STATE.exists():
        return None

    return ARKA_STATE.read_bytes()


def _restore_runtime_state(snapshot: bytes | None) -> None:
    """
    Restore arka_state.json after integrated arka_reply() smoke tests.

    Uses raw bytes to preserve the file exactly.
    """

    if snapshot is None:
        return

    ARKA_STATE.write_bytes(snapshot)
    print("[OK] Restored arka_state.json after smoke test")



def main() -> int:
    _add_paths()
    _compile_targets()

    validator_module = _load_validator_module()
    profile_loader_module = _load_profile_loader_module()
    source_router_module = _load_source_router_module()
    source_execution_bridge_module = _load_source_execution_bridge_module()
    context_builder_module = _load_context_builder_module()

    _test_phase7_source_execution_bridge(context_builder_module, source_execution_bridge_module)
    _test_phase6_source_routes(context_builder_module)
    _test_profile_backed_context(context_builder_module)
    _test_direct_validator_pass(validator_module)
    _test_direct_validator_fail(validator_module)

    state_snapshot = _snapshot_runtime_state()

    try:
        runtime = _load_arka_runtime()

        _test_integrated_pipeline_repairs_bad_identity(runtime)
        _test_integrated_pipeline_repairs_bad_son_identity(runtime)
        _test_integrated_pipeline_repairs_bad_wife_identity(runtime)
        _test_integrated_pipeline_repairs_missing_web_source(runtime)
        _test_integrated_pipeline_repairs_missing_astraa_status_source(runtime)
        _test_integrated_pipeline_uses_git_source_execution(runtime)
        _test_integrated_pipeline_repairs_missing_github_source(runtime)
        _test_integrated_pipeline_allows_good_identity(runtime)
    finally:
        _restore_runtime_state(state_snapshot)

    print("")
    print("[OK] Arka response validation, repair, context, profile, family repair, source-aware routing, source execution, and evidence formatting smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
