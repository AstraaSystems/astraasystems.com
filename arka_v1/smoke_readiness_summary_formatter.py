"""
smoke_readiness_summary_formatter.py

Phase 18B smoke proof for readiness_summary_formatter.py.

This proves Phase 18 converts Phase 17 readiness reports into
safe founder/user-facing summaries.

It does not:
- execute tools
- run shell commands
- call connectors
- enable capabilities
- mutate memory
- write runtime state
- fabricate results
- expose secrets
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
    "readiness_summary_formatter": ARKA_DIR / "core" / "readiness_summary_formatter.py",
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
    print("[OK] Compile passed for Phase 18 readiness summary dependencies")


def load_all():
    registry = load_module("capability_registry_phase18", FILES["capability_registry"])
    sys.modules["core.capability_registry"] = registry

    contracts = load_module(
        "capability_enablement_contracts_phase18",
        FILES["capability_enablement_contracts"],
    )
    sys.modules["core.capability_enablement_contracts"] = contracts

    readiness = load_module(
        "capability_readiness_reporter_phase18",
        FILES["capability_readiness_reporter"],
    )
    sys.modules["core.capability_readiness_reporter"] = readiness

    formatter = load_module(
        "readiness_summary_formatter_phase18",
        FILES["readiness_summary_formatter"],
    )
    sys.modules["core.readiness_summary_formatter"] = formatter

    print("[OK] Loaded Phase 18 readiness summary dependencies directly by file path")

    return formatter


def check_safe_metadata(result):
    metadata = result.metadata

    assert metadata["external_calls"] is False, result
    assert metadata["memory_mutation"] is False, result
    assert metadata["tool_execution"] is False, result
    assert metadata["runtime_writes"] is False, result
    assert metadata["capability_enablement"] is False, result
    assert metadata["connector_execution"] is False, result
    assert metadata["fabricated_results"] is False, result
    assert metadata["secret_exposure"] is False, result


def main():
    compile_all()
    formatter = load_all()

    web = formatter.format_capability_readiness_summary("web_source_placeholder")
    print("")
    print("WEB SUMMARY:")
    print(web.summary)

    assert web.formatted is True, web
    assert web.capability_name == "web_source_placeholder", web
    assert web.status == "not_ready", web
    assert web.missing_requirement_count > 0, web
    assert "Not ready" in web.summary, web.summary
    assert "Missing requirements" in web.summary, web.summary
    assert "do not enable" in web.summary.lower(), web.summary
    check_safe_metadata(web)

    payment = formatter.format_capability_readiness_summary("payment_status_placeholder")
    print("")
    print("PAYMENT SUMMARY:")
    print(payment.summary)

    assert payment.formatted is True, payment
    assert payment.capability_name == "payment_status_placeholder", payment
    assert payment.status == "approval_required", payment
    assert payment.requires_approval is True, payment
    assert "Approval" in payment.summary, payment.summary
    assert "required" in payment.summary.lower(), payment.summary
    check_safe_metadata(payment)

    action = formatter.format_capability_readiness_summary("action_verification_placeholder")
    print("")
    print("ACTION SUMMARY:")
    print(action.summary)

    assert action.formatted is True, action
    assert action.capability_name == "action_verification_placeholder", action
    assert action.status == "mutation_future_only", action
    assert action.allows_mutation is True, action
    assert "future mutation" in action.summary.lower(), action.summary
    assert "must not be enabled" in action.summary.lower(), action.summary
    check_safe_metadata(action)

    git_ready = formatter.format_capability_readiness_summary(
        "local_git_readonly",
        [
            "safe_git_readonly_executor",
            "unsafe_git_action_guard",
            "git_evidence_schema",
        ],
    )
    print("")
    print("GIT READY SUMMARY:")
    print(git_ready.summary)

    assert git_ready.formatted is True, git_ready
    assert git_ready.capability_name == "local_git_readonly", git_ready
    assert git_ready.status == "ready", git_ready
    assert git_ready.missing_requirement_count == 0, git_ready
    assert "Ready" in git_ready.summary, git_ready.summary
    assert "contract-ready" in git_ready.summary, git_ready.summary
    check_safe_metadata(git_ready)

    git_missing = formatter.format_capability_readiness_summary("local_git_readonly")
    print("")
    print("GIT MISSING SUMMARY:")
    print(git_missing.summary)

    assert git_missing.formatted is True, git_missing
    assert git_missing.status == "not_ready", git_missing
    assert git_missing.missing_requirement_count == 3, git_missing
    assert "Missing requirements" in git_missing.summary, git_missing.summary
    check_safe_metadata(git_missing)

    unknown = formatter.format_capability_readiness_summary("unknown_capability")
    print("")
    print("UNKNOWN SUMMARY:")
    print(unknown.summary)

    assert unknown.formatted is False, unknown
    assert "No readiness report" in unknown.summary, unknown.summary
    check_safe_metadata(unknown)

    all_summary = formatter.format_all_readiness_summaries(
        include_missing_requirements=True,
    )
    print("")
    print("ALL SUMMARY:")
    print(all_summary.summary)

    assert all_summary.formatted is True, all_summary
    assert "Capability readiness summary" in all_summary.summary, all_summary.summary
    assert "Ready:" in all_summary.summary, all_summary.summary
    assert "Not ready:" in all_summary.summary, all_summary.summary
    assert "Approval required:" in all_summary.summary, all_summary.summary
    assert "Future mutation only:" in all_summary.summary, all_summary.summary
    assert "No capabilities were enabled" in all_summary.summary, all_summary.summary
    check_safe_metadata(all_summary)

    print("")
    print("[OK] Phase 18 readiness summary formatter smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
