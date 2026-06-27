"""
smoke_capability_registry.py

Phase 11B smoke proof for Arka capability registry.

This test proves capability_registry.py returns safe route-to-capability
decisions for enabled, disabled, read-only, placeholder, and approval-required
capabilities.

It does not:
- execute tools
- run shell commands
- mutate memory
- write runtime state
- approve destructive actions
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ARKA_DIR = Path(__file__).resolve().parent
CAPABILITY_REGISTRY = ARKA_DIR / "core" / "capability_registry.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def compile_all():
    py_compile.compile(str(CAPABILITY_REGISTRY), doraise=True)
    print("[OK] Compile passed for Phase 11 capability registry")


def check_route(
    registry,
    route,
    expected_name,
    expected_enabled,
    expected_read_only,
    expected_requires_approval,
):
    decision = registry.find_capability_for_route(route)
    data = decision.to_dict()

    print("")
    print("ROUTE:", route)
    print("capability:", data["capability_name"])
    print("enabled:", data["enabled"])
    print("read_only:", data["read_only"])
    print("mutates_state:", data["mutates_state"])
    print("requires_approval:", data["requires_approval"])
    print("warnings:", data["warnings"])

    assert data["matched"] is True, data
    assert data["capability_name"] == expected_name, data
    assert data["enabled"] is expected_enabled, data
    assert data["read_only"] is expected_read_only, data
    assert data["mutates_state"] is False, data
    assert data["requires_approval"] is expected_requires_approval, data
    assert data["metadata"]["tool_execution"] is False, data
    assert data["metadata"]["runtime_writes"] is False, data
    assert data["metadata"]["destructive_actions_allowed"] is False, data

    if expected_enabled is False:
        assert "capability_registered_but_disabled" in data["warnings"], data

    if expected_requires_approval:
        assert "capability_requires_approval" in data["warnings"], data


def main():
    compile_all()

    registry = load_module(
        "capability_registry_phase11_smoke",
        CAPABILITY_REGISTRY,
    )

    capabilities = registry.list_capabilities()
    print("capability_count:", len(capabilities))
    assert len(capabilities) >= 8, capabilities

    local_git = registry.get_capability("local_git_readonly")
    assert local_git is not None, local_git
    assert local_git["enabled"] is True, local_git
    assert local_git["read_only"] is True, local_git
    assert local_git["mutates_state"] is False, local_git
    assert local_git["requires_approval"] is False, local_git

    check_route(
        registry,
        "LOCAL_PROFILE",
        "profile_context",
        True,
        True,
        False,
    )

    check_route(
        registry,
        "GITHUB_REQUIRED",
        "local_git_readonly",
        True,
        True,
        False,
    )

    check_route(
        registry,
        "WEB_SOURCE_REQUIRED",
        "web_source_placeholder",
        False,
        True,
        False,
    )

    check_route(
        registry,
        "ASTRAA_STATUS_REQUIRED",
        "astraa_status_placeholder",
        False,
        True,
        False,
    )

    check_route(
        registry,
        "SERVER_REQUIRED",
        "server_health_placeholder",
        False,
        True,
        False,
    )

    check_route(
        registry,
        "PAYMENT_REQUIRED",
        "payment_status_placeholder",
        False,
        True,
        False,
    )

    check_route(
        registry,
        "ACTION_VERIFICATION_REQUIRED",
        "action_verification_placeholder",
        False,
        True,
        True,
    )

    context_decision = registry.decide_capability_for_context({
        "source_route": {
            "route": "GITHUB_REQUIRED",
        }
    })

    assert context_decision.capability_name == "local_git_readonly", context_decision
    assert context_decision.enabled is True, context_decision
    assert context_decision.read_only is True, context_decision

    missing = registry.find_capability_for_route("UNKNOWN_ROUTE").to_dict()

    print("")
    print("ROUTE: UNKNOWN_ROUTE")
    print("decision:", missing)

    assert missing["matched"] is False, missing
    assert "capability_not_registered" in missing["warnings"], missing

    print("")
    print("[OK] Phase 11 capability registry smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
