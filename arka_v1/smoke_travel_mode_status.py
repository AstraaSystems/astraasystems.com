"""
smoke_travel_mode_status.py

Phase 19B smoke proof for travel_mode_status.py.

This proves Phase 19 can build a safe Travel / Delivery Mode operational
dashboard using supplied checkpoint values and Phase 18 readiness summaries.

It does not:
- execute shell commands
- mutate Git
- call connectors
- enable capabilities
- write runtime state
- expose secrets
- fabricate live server/web/payment status
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
    "travel_mode_status": ARKA_DIR / "core" / "travel_mode_status.py",
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
    print("[OK] Compile passed for Phase 19 travel mode status dependencies")


def load_all():
    registry = load_module("capability_registry_phase19", FILES["capability_registry"])
    sys.modules["core.capability_registry"] = registry

    contracts = load_module(
        "capability_enablement_contracts_phase19",
        FILES["capability_enablement_contracts"],
    )
    sys.modules["core.capability_enablement_contracts"] = contracts

    readiness = load_module(
        "capability_readiness_reporter_phase19",
        FILES["capability_readiness_reporter"],
    )
    sys.modules["core.capability_readiness_reporter"] = readiness

    formatter = load_module(
        "readiness_summary_formatter_phase19",
        FILES["readiness_summary_formatter"],
    )
    sys.modules["core.readiness_summary_formatter"] = formatter

    travel = load_module(
        "travel_mode_status_phase19",
        FILES["travel_mode_status"],
    )
    sys.modules["core.travel_mode_status"] = travel

    print("[OK] Loaded Phase 19 travel mode dependencies directly by file path")

    return travel


def check_safe_metadata(metadata):
    assert metadata["external_calls"] is False, metadata
    assert metadata["shell_execution"] is False, metadata
    assert metadata["git_mutation"] is False, metadata
    assert metadata["memory_mutation"] is False, metadata
    assert metadata["runtime_writes"] is False, metadata
    assert metadata["tool_execution"] is False, metadata
    assert metadata["connector_execution"] is False, metadata
    assert metadata["capability_enablement"] is False, metadata
    assert metadata["secret_exposure"] is False, metadata
    assert metadata["fabricated_results"] is False, metadata


def main():
    compile_all()
    travel = load_all()

    status = travel.build_travel_mode_status(
        current_commit="c70c473",
        current_tag="arka-v1-readiness-summary-formatter-smoke-20260625",
        proof_branch="arka-v1-readiness-summary-proof-20260625",
        bundle_path="/mnt/d/ARKA_HQ/migration_backups_20260625/arka_hq_phase18_readiness_summary_stable_20260625.bundle",
        source_of_truth="DESKTOP-K930S6S",
        remote_context="Langford travel laptop to main PC remote",
        extra_warnings=[
            "Langford remote access path is active.",
        ],
    )

    data = status.to_dict()

    print("")
    print("STATUS DICT:")
    print(data)

    assert data["mode"] == "Travel / Delivery Mode", data
    assert data["source_of_truth"] == "DESKTOP-K930S6S", data
    assert data["remote_context"] == "Langford travel laptop to main PC remote", data
    assert data["current_commit"] == "c70c473", data
    assert data["current_tag"] == "arka-v1-readiness-summary-formatter-smoke-20260625", data
    assert data["proof_branch"] == "arka-v1-readiness-summary-proof-20260625", data
    assert "arka_hq_phase18_readiness_summary_stable_20260625.bundle" in data["bundle_path"], data

    assert "Capability readiness summary" in data["readiness_summary"], data
    assert isinstance(data["ready_count"], int), data
    assert isinstance(data["not_ready_count"], int), data
    assert isinstance(data["approval_required_count"], int), data
    assert isinstance(data["mutation_future_only_count"], int), data

    assert "Use DESKTOP-K930S6S main PC as the Arka HQ source of truth." in data["warnings"], data
    assert "Do not copy secrets, payment data, runtime state, or private memory to the travel laptop." in data["warnings"], data
    assert "Langford remote access path is active." in data["warnings"], data

    assert "Real Arka HQ work should happen through the remote main PC WSL repo." in data["safe_operating_rules"], data

    check_safe_metadata(data["metadata"])

    text = travel.format_travel_mode_status_text(status)

    print("")
    print("STATUS TEXT:")
    print(text)

    assert "Arka Travel / Delivery Mode Status" in text, text
    assert "Source of truth: DESKTOP-K930S6S" in text, text
    assert "Remote context: Langford travel laptop to main PC remote" in text, text
    assert "Current checkpoint: c70c473" in text, text
    assert "Stable tag: arka-v1-readiness-summary-formatter-smoke-20260625" in text, text
    assert "Proof branch: arka-v1-readiness-summary-proof-20260625" in text, text
    assert "Capability readiness:" in text, text
    assert "Safe operating rules:" in text, text
    assert "Warnings:" in text, text
    assert "No tools, connectors, capabilities, runtime state, or secrets were executed or modified" in text, text

    text2 = travel.build_and_format_travel_mode_status(
        current_commit="c70c473",
        current_tag="arka-v1-readiness-summary-formatter-smoke-20260625",
        proof_branch="arka-v1-readiness-summary-proof-20260625",
        bundle_path="/mnt/d/ARKA_HQ/migration_backups_20260625/arka_hq_phase18_readiness_summary_stable_20260625.bundle",
    )

    assert "Arka Travel / Delivery Mode Status" in text2, text2
    assert "No tools, connectors, capabilities, runtime state, or secrets were executed or modified" in text2, text2

    print("")
    print("[OK] Phase 19 travel mode status smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
