"""
smoke_capability_enablement_contracts.py

Phase 15B smoke proof for capability_enablement_contracts.py.

This proves:
- disabled placeholders cannot be enabled casually
- payment/action contracts require approval
- local_git_readonly can enable only when safety components are present
- unknown capabilities are rejected safely

No tool execution. No shell execution. No runtime writes.
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ARKA_DIR = Path(__file__).resolve().parent
CONTRACTS_FILE = ARKA_DIR / "core" / "capability_enablement_contracts.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_disabled(module, capability_name, expected_route, expected_approval):
    contract = module.get_enablement_contract(capability_name)
    decision = module.evaluate_enablement(capability_name, [])

    print("")
    print("CAPABILITY:", capability_name)
    print("route:", decision.route)
    print("can_enable:", decision.can_enable)
    print("requires_approval:", decision.requires_approval)
    print("missing:", decision.missing_requirements)
    print("warnings:", decision.warnings)

    assert contract is not None, capability_name
    assert contract["route"] == expected_route, contract
    assert decision.can_enable is False, decision
    assert decision.route == expected_route, decision
    assert decision.requires_approval is expected_approval, decision
    assert "missing_required_components" in decision.warnings, decision
    assert decision.metadata["tool_execution"] is False, decision
    assert decision.metadata["runtime_writes"] is False, decision
    assert decision.metadata["destructive_actions_allowed"] is False, decision
    assert decision.metadata["fabricated_results"] is False, decision


def main():
    py_compile.compile(str(CONTRACTS_FILE), doraise=True)
    print("[OK] Compile passed for Phase 15 enablement contracts")

    module = load_module("capability_enablement_contracts_phase15_smoke", CONTRACTS_FILE)

    contracts = module.list_enablement_contracts()
    print("contract_count:", len(contracts))
    assert len(contracts) >= 7, contracts

    check_disabled(module, "web_source_placeholder", "WEB_SOURCE_REQUIRED", False)
    check_disabled(module, "astraa_status_placeholder", "ASTRAA_STATUS_REQUIRED", False)
    check_disabled(module, "server_health_placeholder", "SERVER_REQUIRED", False)
    check_disabled(module, "payment_status_placeholder", "PAYMENT_REQUIRED", True)
    check_disabled(module, "math_executor_placeholder", "MATH_REQUIRED", False)
    check_disabled(module, "action_verification_placeholder", "ACTION_VERIFICATION_REQUIRED", True)

    git_missing = module.evaluate_enablement("local_git_readonly", [])
    print("")
    print("CAPABILITY: local_git_readonly without components")
    print("can_enable:", git_missing.can_enable)
    print("missing:", git_missing.missing_requirements)

    assert git_missing.can_enable is False, git_missing
    assert "missing_required_components" in git_missing.warnings, git_missing

    git_components = [
        "safe_git_readonly_executor",
        "unsafe_git_action_guard",
        "git_evidence_schema",
    ]

    git_ready = module.evaluate_enablement("local_git_readonly", git_components)
    print("")
    print("CAPABILITY: local_git_readonly with safety components")
    print("can_enable:", git_ready.can_enable)
    print("warnings:", git_ready.warnings)

    assert git_ready.can_enable is True, git_ready
    assert git_ready.requires_approval is False, git_ready
    assert git_ready.allows_mutation is False, git_ready
    assert git_ready.read_only_required is True, git_ready

    payment_route = module.evaluate_route_enablement("PAYMENT_REQUIRED", [])
    print("")
    print("ROUTE: PAYMENT_REQUIRED")
    print("capability:", payment_route.capability_name)
    print("requires_approval:", payment_route.requires_approval)

    assert payment_route.capability_name == "payment_status_placeholder", payment_route
    assert payment_route.requires_approval is True, payment_route
    assert payment_route.can_enable is False, payment_route

    unknown = module.evaluate_enablement("unknown_capability", [])
    print("")
    print("CAPABILITY: unknown_capability")
    print("can_enable:", unknown.can_enable)
    print("warnings:", unknown.warnings)

    assert unknown.can_enable is False, unknown
    assert "enablement_contract_not_registered" in unknown.warnings, unknown

    for contract in contracts:
        assert contract["metadata"]["phase"] == "phase15", contract

    print("")
    print("[OK] Phase 15 capability enablement contracts smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
