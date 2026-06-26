#!/usr/bin/env python3
"""
smoke_response_validator_integration.py

Smoke test for Arka Phase 1 response validator integration.

This test verifies:
1. response_validator.py compiles
2. arka_v1.py compiles
3. direct validator PASS behavior
4. direct validator FAIL behavior
5. integrated arka_reply() blocks a bad identity response
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


def _test_integrated_pipeline_blocks_bad_identity(runtime: ModuleType) -> None:
    """
    Integrated pipeline test.

    Monkeypatch governor dispatch to return a bad identity response.
    arka_reply() should pass it through Phase 1 validation and block it.
    """

    def fake_bad_dispatch(raw: str, web_func=None) -> str:
        return "I could not pull reliable live snippets."

    runtime.arka_governor_dispatch = fake_bad_dispatch

    response = runtime.arka_reply("who am I?")

    assert isinstance(response, str), type(response)
    assert "Phase 1 validation" in response, response
    assert "OWNER_IDENTITY_CONFUSION" in response, response

    print("[OK] Integrated pipeline blocks bad identity response")


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


def _snapshot_runtime_state() -> str | None:
    """
    Snapshot arka_state.json so smoke tests do not leave runtime log changes.
    """

    if not ARKA_STATE.exists():
        return None

    return ARKA_STATE.read_text(encoding="utf-8")


def _restore_runtime_state(snapshot: str | None) -> None:
    """
    Restore arka_state.json after integrated arka_reply() smoke tests.
    """

    if snapshot is None:
        return

    ARKA_STATE.write_text(snapshot, encoding="utf-8")
    print("[OK] Restored arka_state.json after smoke test")



def main() -> int:
    _add_paths()
    _compile_targets()

    validator_module = _load_validator_module()

    _test_direct_validator_pass(validator_module)
    _test_direct_validator_fail(validator_module)

    state_snapshot = _snapshot_runtime_state()

    try:
        runtime = _load_arka_runtime()

        _test_integrated_pipeline_blocks_bad_identity(runtime)
        _test_integrated_pipeline_allows_good_identity(runtime)
    finally:
        _restore_runtime_state(state_snapshot)

    print("")
    print("[OK] Arka Phase 1 response validator integration smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
