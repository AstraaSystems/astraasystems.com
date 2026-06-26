#!/usr/bin/env python3
"""
smoke_response_validator_integration.py

Smoke test for Arka Phase 1 response validator integration.

This test verifies both:
1. Direct validator behavior
2. Actual arka_reply() pipeline behavior after governor dispatch

It intentionally monkeypatches arka_governor_dispatch so we can test the
validator integration without depending on live web, routes, or external tools.
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARKA_DIR = ROOT / "arka_v1"
ARKA_APP = ARKA_DIR / "arka_v1.py"
VALIDATOR = ARKA_DIR / "core" / "response_validator.py"


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


def _load_arka_runtime():
    """
    Load arka_v1.py as an isolated runtime module.

    We avoid normal package import here because the repo has both:
    - arka_v1/ directory
    - arka_v1/arka_v1.py file
    """

    spec = importlib.util.spec_from_file_location("arka_runtime_smoke", ARKA_APP)

    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create import spec for arka_v1.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "arka_reply"):
        raise RuntimeError("arka_v1.py does not expose arka_reply(raw)")

    if not hasattr(module, "arka_governor_dispatch"):
        raise RuntimeError("arka_v1.py does not expose arka_governor_dispatch")

    print("[OK] Loaded arka_v1.py runtime module")

    return module


def _test_direct_validator_pass() -> None:
    """
    Direct validator PASS test.
    """

    try:
        from arka_v1.core.response_validator import validate_response, ValidationStatus
    except Exception:
        from core.response_validator import validate_response, ValidationStatus

    result = validate_response(
        prompt="who am I?",
        response="You are Keshanth Sivayogampillai.",
        context={
            "owner_name": "Keshanth Sivayogampillai",
            "requires_source": False,
            "sources": [],
        },
        strict_mode=True,
    )

    assert result.status == ValidationStatus.PASS, result
    assert result.ok is True, result
    assert result.issues == [], result.issues

    print("[OK] Direct validator PASS case works")


def _test_direct_validator_fail() -> None:
    """
    Direct validator FAIL test.
    """

    try:
        from arka_v1.core.response_validator import validate_response, ValidationStatus
    except Exception:
        from core.response_validator import validate_response, ValidationStatus

    result = validate_response(
        prompt="who am I?",
        response="I could not pull reliable live snippets.",
        context={
            "owner_name": "Keshanth Sivayogampillai",
        },
        strict_mode=True,
    )

    issue_codes = [issue.code for issue in result.issues]

    assert result.status == ValidationStatus.FAIL, result
    assert result.ok is False, result
    assert "OWNER_IDENTITY_CONFUSION" in issue_codes, issue_codes

    print("[OK] Direct validator FAIL case works")


def _test_integrated_pipeline_blocks_bad_identity(runtime) -> None:
    """
    Integrated pipeline test.

    Monkeypatch governor dispatch to return a bad identity response.
    arka_reply() should pass it through the Phase 1 validator and block it.
    """

    def fake_bad_dispatch(raw: str, web_func=None) -> str:
        return "I could not pull reliable live snippets."

    runtime.arka_governor_dispatch = fake_bad_dispatch

    response = runtime.arka_reply("who am I?")

    assert isinstance(response, str), type(response)
    assert "Phase 1 validation" in response, response
    assert "OWNER_IDENTITY_CONFUSION" in response, response

    print("[OK] Integrated pipeline blocks bad identity response")


def _test_integrated_pipeline_allows_good_identity(runtime) -> None:
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


def main() -> int:
    _add_paths()
    _compile_targets()

    _test_direct_validator_pass()
    _test_direct_validator_fail()

    runtime = _load_arka_runtime()

    _test_integrated_pipeline_blocks_bad_identity(runtime)
    _test_integrated_pipeline_allows_good_identity(runtime)

    print("")
    print("[OK] Arka Phase 1 response validator integration smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
