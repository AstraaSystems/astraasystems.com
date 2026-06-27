"""
smoke_capability_limitation_integration.py

Phase 14C integration smoke proof for capability limitation formatter.

This test proves runtime arka_reply() uses capability_limitation_formatter.py
to produce clean user-facing limitation messages for disabled/blocked capabilities.

It does not:
- execute destructive tools
- mutate memory permanently
- write runtime state permanently
- fabricate web/Astraa/server/payment results
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path
from types import ModuleType


ARKA_DIR = Path(__file__).resolve().parent
STATE_FILE = ARKA_DIR / "arka_state.json"

FILES = {
    "profile_loader": ARKA_DIR / "core" / "profile_loader.py",
    "source_router": ARKA_DIR / "core" / "source_router.py",
    "context_builder": ARKA_DIR / "core" / "context_builder.py",
    "capability_registry": ARKA_DIR / "core" / "capability_registry.py",
    "source_execution_bridge": ARKA_DIR / "core" / "source_execution_bridge.py",
    "response_validator": ARKA_DIR / "core" / "response_validator.py",
    "response_repairer": ARKA_DIR / "core" / "response_repairer.py",
    "evidence_response_formatter": ARKA_DIR / "core" / "evidence_response_formatter.py",
    "response_policy": ARKA_DIR / "core" / "response_policy.py",
    "policy_observer": ARKA_DIR / "core" / "policy_observer.py",
    "capability_limitation_formatter": ARKA_DIR / "core" / "capability_limitation_formatter.py",
    "arka_runtime": ARKA_DIR / "arka_v1.py",
}


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def compile_all() -> None:
    for path in FILES.values():
        py_compile.compile(str(path), doraise=True)

    print("[OK] Compile passed for Phase 14C limitation integration dependencies")


def snapshot_state():
    if not STATE_FILE.exists():
        return None
    return STATE_FILE.read_bytes()


def restore_state(snapshot) -> None:
    if snapshot is None:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        return

    STATE_FILE.write_bytes(snapshot)
    print("[OK] Restored arka_state.json after Phase 14C smoke test")


def load_runtime() -> ModuleType:
    profile_loader = load_module("profile_loader_phase14c", FILES["profile_loader"])
    sys.modules["core.profile_loader"] = profile_loader

    source_router = load_module("source_router_phase14c", FILES["source_router"])
    sys.modules["core.source_router"] = source_router

    capability_registry = load_module(
        "capability_registry_phase14c",
        FILES["capability_registry"],
    )
    sys.modules["core.capability_registry"] = capability_registry

    context_builder = load_module("context_builder_phase14c", FILES["context_builder"])
    sys.modules["core.context_builder"] = context_builder

    source_execution_bridge = load_module(
        "source_execution_bridge_phase14c",
        FILES["source_execution_bridge"],
    )
    sys.modules["core.source_execution_bridge"] = source_execution_bridge

    response_validator = load_module(
        "response_validator_phase14c",
        FILES["response_validator"],
    )
    sys.modules["core.response_validator"] = response_validator

    response_repairer = load_module(
        "response_repairer_phase14c",
        FILES["response_repairer"],
    )
    sys.modules["core.response_repairer"] = response_repairer

    evidence_formatter = load_module(
        "evidence_response_formatter_phase14c",
        FILES["evidence_response_formatter"],
    )
    sys.modules["core.evidence_response_formatter"] = evidence_formatter

    response_policy = load_module(
        "response_policy_phase14c",
        FILES["response_policy"],
    )
    sys.modules["core.response_policy"] = response_policy

    policy_observer = load_module(
        "policy_observer_phase14c",
        FILES["policy_observer"],
    )
    sys.modules["core.policy_observer"] = policy_observer

    limitation_formatter = load_module(
        "capability_limitation_formatter_phase14c",
        FILES["capability_limitation_formatter"],
    )
    sys.modules["core.capability_limitation_formatter"] = limitation_formatter

    runtime = load_module("arka_runtime_phase14c", FILES["arka_runtime"])

    print("[OK] Loaded Arka runtime for Phase 14C limitation integration smoke")

    return runtime


def set_generic_governor(runtime: ModuleType) -> None:
    def fake_governor_response(raw: str, web_func=None) -> str:
        return "Generic pre-format response."

    runtime.arka_governor_dispatch = fake_governor_response


def assert_contains(response: str, expected_parts):
    for part in expected_parts:
        assert part in response, response


def assert_not_contains(response: str, forbidden_parts):
    lowered = response.lower()
    for part in forbidden_parts:
        assert part.lower() not in lowered, response


def check_runtime_limitation(
    runtime: ModuleType,
    prompt: str,
    expected_parts,
    forbidden_parts=None,
) -> None:
    forbidden_parts = forbidden_parts or []

    response = runtime.arka_reply(prompt)

    print("")
    print("PROMPT:", prompt)
    print("RESPONSE:")
    print(response)

    assert isinstance(response, str), type(response)
    assert_contains(response, expected_parts)
    assert_not_contains(response, forbidden_parts)


def test_disabled_web(runtime: ModuleType) -> None:
    check_runtime_limitation(
        runtime,
        "do a web search about how to cook rice",
        [
            "I can’t perform a live web lookup",
            "web source capability is registered",
            "currently disabled",
            "I won’t make up a web-sourced answer",
        ],
        [
            "according to web results",
            "I found online",
        ],
    )

    print("[OK] Runtime formats disabled web capability limitation")


def test_disabled_astraa(runtime: ModuleType) -> None:
    check_runtime_limitation(
        runtime,
        "check astraasystems.com website status",
        [
            "I can’t verify Astraa website/app status",
            "Astraa status capability is registered",
            "currently disabled",
            "without verified evidence",
        ],
        [
            "the site is up",
            "the site is down",
        ],
    )

    print("[OK] Runtime formats disabled Astraa status capability limitation")


def test_disabled_server(runtime: ModuleType) -> None:
    check_runtime_limitation(
        runtime,
        "is the backend server healthy?",
        [
            "I can’t check backend/server health",
            "server health capability is registered",
            "currently disabled",
            "without verified evidence",
        ],
        [
            "server is healthy",
            "server is down",
        ],
    )

    print("[OK] Runtime formats disabled server health capability limitation")


def test_disabled_payment(runtime: ModuleType) -> None:
    check_runtime_limitation(
        runtime,
        "check Moneris payment status",
        [
            "I can’t check payment or Moneris status",
            "payment status capability is registered",
            "currently disabled",
            "without verified evidence",
        ],
        [
            "payment succeeded",
            "payment failed",
        ],
    )

    print("[OK] Runtime formats disabled payment capability limitation")


def test_unsafe_git_action(runtime: ModuleType) -> None:
    check_runtime_limitation(
        runtime,
        "git push origin main",
        [
            "I can inspect Git safely",
            "I won’t run or claim a Git action",
            "No Git action was performed",
        ],
        [
            "pushed to origin",
            "push completed",
        ],
    )

    print("[OK] Runtime formats unsafe Git action limitation")


def test_successful_git_not_limitation(runtime: ModuleType) -> None:
    response = runtime.arka_reply("show git status")

    print("")
    print("PROMPT: show git status")
    print("RESPONSE:")
    print(response)

    assert isinstance(response, str), type(response)
    assert "Source: local_git" in response, response
    assert "No Git action was performed" not in response, response
    assert "currently disabled" not in response, response

    print("[OK] Runtime does not limitation-format successful Git evidence")


def main() -> int:
    compile_all()

    snapshot = snapshot_state()

    try:
        runtime = load_runtime()
        set_generic_governor(runtime)

        test_disabled_web(runtime)
        test_disabled_astraa(runtime)
        test_disabled_server(runtime)
        test_disabled_payment(runtime)
        test_unsafe_git_action(runtime)
        test_successful_git_not_limitation(runtime)

    finally:
        restore_state(snapshot)

    print("")
    print("[OK] Phase 14C capability limitation runtime integration smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
