"""
smoke_capability_readiness_reporter.py

Phase 17B smoke proof for capability_readiness_reporter.py.

This proves readiness reporting combines:
- capability_registry.py
- capability_enablement_contracts.py

No tool execution. No connector execution. No runtime writes.
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ARKA_DIR = Path(__file__).resolve().parent

FILES = {
    "capability_registry": ARKA_DIR / "core" / "capability_registry.py",
    "capability_enablement_contracts": ARKA_DIR / "core" / "capability_enablement_contracts.py",
    "capability_readiness_reporter": ARKA_DIR / "core" / "capability_readiness_reporter.py",
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
    print("[OK] Compile passed for Phase 17 capability readiness dependencies")


def load_all():
    registry = load_module("capability_registry_phase17", FILES["capability_registry"])
    sys.modules["core.capability_registry"] = registry

    contracts = load_module(
        "capability_enablement_contracts_phase17",
        FILES["capability_enablement_contracts"],
    )
    sys.modules["core.capability_enablement_contracts"] = contracts

    reporter = load_module(
        "capability_readiness_reporter_phase17",
        FILES["capability_readiness_reporter"],
    )
    sys.modules["core.capability_readiness_reporter"] = reporter

    print("[OK] Loaded Phase 17 readiness dependencies directly by file path")

    return reporter


def check_report_common(item):
    assert item is not None, item
    assert item["metadata"]["tool_execution"] is False, item
    assert item["metadata"]["runtime_writes"] is False, item
    assert item["metadata"]["capability_enablement"] is False, item
    assert item["metadata"]["fabricated_results"] is False, item


def main():
    compile_all()
    reporter = load_all()

    reports = reporter.list_capability_readiness()
    print("report_count:", len(reports))
    assert len(reports) >= 7, reports

    web = reporter.get_capability_readiness("web_source_placeholder")
    print("")
    print("WEB:", web)
    check_report_common(web)
    assert web["status"] == "not_ready", web
    assert web["registry_enabled"] is False, web
    assert web["contract_exists"] is True, web
    assert web["missing_requirement_count"] > 0, web

    payment = reporter.get_capability_readiness("payment_status_placeholder")
    print("")
    print("PAYMENT:", payment)
    check_report_common(payment)
    assert payment["status"] == "approval_required", payment
    assert payment["requires_approval"] is True, payment
    assert payment["missing_requirement_count"] > 0, payment

    action = reporter.get_capability_readiness("action_verification_placeholder")
    print("")
    print("ACTION:", action)
    check_report_common(action)
    assert action["status"] == "mutation_future_only", action
    assert action["requires_approval"] is True, action
    assert action["contract_exists"] is True, action

    git_missing = reporter.get_capability_readiness("local_git_readonly")
    print("")
    print("GIT without components:", git_missing)
    check_report_common(git_missing)
    assert git_missing["registry_enabled"] is True, git_missing
    assert git_missing["status"] == "not_ready", git_missing
    assert git_missing["missing_requirement_count"] == 3, git_missing

    git_ready = reporter.get_capability_readiness(
        "local_git_readonly",
        [
            "safe_git_readonly_executor",
            "unsafe_git_action_guard",
            "git_evidence_schema",
        ],
    )
    print("")
    print("GIT with components:", git_ready)
    check_report_common(git_ready)
    assert git_ready["status"] == "ready", git_ready
    assert git_ready["can_enable"] is True, git_ready
    assert git_ready["missing_requirement_count"] == 0, git_ready

    missing = reporter.get_capability_readiness("unknown_capability")
    print("")
    print("UNKNOWN:", missing)
    assert missing is None, missing

    summary = reporter.summarize_capability_readiness()
    print("")
    print("SUMMARY:", summary)
    assert summary["total_capabilities"] >= 7, summary
    assert summary["metadata"]["tool_execution"] is False, summary
    assert summary["metadata"]["runtime_writes"] is False, summary
    assert summary["metadata"]["capability_enablement"] is False, summary

    print("")
    print("[OK] Phase 17 capability readiness reporter smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
