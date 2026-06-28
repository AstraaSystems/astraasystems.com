"""
smoke_release_candidate_status.py

Phase 20B smoke proof for release_candidate_status.py.

This proves Phase 20 can build a safe Arka V1 Travel Stable /
Release Candidate Freeze record using supplied evidence.

It does not:
- execute shell commands
- inspect Git directly
- mutate Git
- call connectors
- check live websites
- check backend servers
- enable capabilities
- write runtime state
- expose secrets
- fabricate live service status
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
from pathlib import Path


ARKA_DIR = Path(__file__).resolve().parent

FILES = {
    "release_candidate_status": ARKA_DIR / "core" / "release_candidate_status.py",
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
    print("[OK] Compile passed for Phase 20 release candidate status dependency")


def load_all():
    release_candidate = load_module(
        "release_candidate_status_phase20",
        FILES["release_candidate_status"],
    )
    sys.modules["core.release_candidate_status"] = release_candidate

    print("[OK] Loaded Phase 20 release candidate status dependency directly by file path")
    return release_candidate


def check_safe_metadata(metadata):
    assert metadata["external_calls"] is False, metadata
    assert metadata["shell_execution"] is False, metadata
    assert metadata["git_mutation"] is False, metadata
    assert metadata["memory_mutation"] is False, metadata
    assert metadata["runtime_writes"] is False, metadata
    assert metadata["tool_execution"] is False, metadata
    assert metadata["connector_execution"] is False, metadata
    assert metadata["capability_enablement"] is False, metadata
    assert metadata["live_service_checks"] is False, metadata
    assert metadata["secret_exposure"] is False, metadata
    assert metadata["fabricated_results"] is False, metadata


def main():
    compile_all()
    release_candidate = load_all()

    smoke_stack_summary = [
        "Phase 15 capability enablement contracts smoke proof passed.",
        "Phase 17 capability readiness reporter smoke proof passed.",
        "Phase 18 readiness summary formatter smoke proof passed.",
        "Phase 19 travel mode status smoke proof passed.",
        "Phase 13 capability observability smoke proof passed.",
        "Phase 14 capability limitation formatter smoke proof passed.",
        "Full response validator integration smoke proof passed.",
    ]

    website_recovery_notes = [
        "Static website/root is working.",
        "Mobile website is working.",
        "Astraa logo hotfix was deployed live to origin/main at e804f1d.",
        "Live site serves 30px logo CSS after hotfix verification.",
        "Backend/API remains a separate follow-up and is not claimed healthy.",
    ]

    known_followups = [
        "Public website visual recovery is complete.",
        "Backend/API/ngrok/server route recovery remains separate from Arka Phase 20 freeze.",
    ]

    status = release_candidate.build_release_candidate_status(
        current_commit="b786c3d",
        stable_tag="arka-v1-travel-mode-status-smoke-20260625",
        proof_branch="arka-v1-travel-mode-status-proof-20260625",
        bundle_path="/mnt/d/ARKA_HQ/migration_backups_20260625/arka_hq_phase19_travel_mode_status_stable_20260625.bundle",
        smoke_stack_passed=True,
        smoke_stack_summary=smoke_stack_summary,
        website_recovery_notes=website_recovery_notes,
        known_followups=known_followups,
        source_of_truth="DESKTOP-K930S6S",
        remote_context="Langford travel laptop to main PC remote",
    )

    data = status.to_dict()

    print("")
    print("RELEASE CANDIDATE STATUS DICT:")
    print(data)

    assert data["release_name"] == "Arka V1 Travel Stable Release Candidate", data
    assert data["mode"] == "Travel Stable / Release Candidate Freeze", data
    assert data["current_commit"] == "b786c3d", data
    assert data["stable_tag"] == "arka-v1-travel-mode-status-smoke-20260625", data
    assert data["proof_branch"] == "arka-v1-travel-mode-status-proof-20260625", data
    assert "phase19_travel_mode_status" in data["bundle_path"], data
    assert data["source_of_truth"] == "DESKTOP-K930S6S", data
    assert data["remote_context"] == "Langford travel laptop to main PC remote", data

    assert data["smoke_stack_passed"] is True, data
    assert data["release_decision"] == "release_candidate_ready", data
    assert data["next_safe_action"] == "Create the Phase 20 smoke proof and final travel-stable bundle.", data

    assert "Phase 19 travel mode status smoke proof passed." in data["smoke_stack_summary"], data
    assert "Astraa logo hotfix was deployed live to origin/main at e804f1d." in data["website_recovery_notes"], data
    assert "Live site serves 30px logo CSS after hotfix verification." in data["website_recovery_notes"], data
    assert "Backend/API remains a separate operational follow-up if tools require live server routes." in data["known_followups"], data
    assert "Backend/API/ngrok/server route recovery remains separate from Arka Phase 20 freeze." in data["known_followups"], data

    assert "Arka V1 response/capability/travel spine through Phase 19." in data["freeze_scope"], data
    assert "New backend/server health implementation." in data["out_of_scope"], data
    assert "No shell commands are executed by this module." in data["safety_boundaries"], data
    assert "No live website, payment, backend, or server status is claimed without supplied evidence." in data["safety_boundaries"], data

    check_safe_metadata(data["metadata"])

    text = release_candidate.format_release_candidate_status_text(status)

    print("")
    print("RELEASE CANDIDATE STATUS TEXT:")
    print(text)

    assert "Arka V1 Travel Stable Release Candidate Status" in text, text
    assert "Current commit: b786c3d" in text, text
    assert "Stable tag: arka-v1-travel-mode-status-smoke-20260625" in text, text
    assert "Proof branch: arka-v1-travel-mode-status-proof-20260625" in text, text
    assert "Smoke stack passed: True" in text, text
    assert "Release decision: release_candidate_ready" in text, text
    assert "Static website/root is working." in text, text
    assert "Backend/API remains a separate follow-up and is not claimed healthy." in text, text
    assert "No shell commands, Git actions, connectors, runtime state, capabilities, secrets, or live service checks were executed" in text, text

    text2 = release_candidate.build_and_format_release_candidate_status(
        current_commit="b786c3d",
        stable_tag="arka-v1-travel-mode-status-smoke-20260625",
        proof_branch="arka-v1-travel-mode-status-proof-20260625",
        bundle_path="/mnt/d/ARKA_HQ/migration_backups_20260625/arka_hq_phase19_travel_mode_status_stable_20260625.bundle",
        smoke_stack_passed=True,
        smoke_stack_summary=smoke_stack_summary,
        website_recovery_notes=website_recovery_notes,
        known_followups=known_followups,
    )

    assert "Arka V1 Travel Stable Release Candidate Status" in text2, text2
    assert "release_candidate_ready" in text2, text2

    blocked = release_candidate.build_release_candidate_status(
        current_commit="b786c3d",
        stable_tag="arka-v1-travel-mode-status-smoke-20260625",
        proof_branch="arka-v1-travel-mode-status-proof-20260625",
        bundle_path="/mnt/d/ARKA_HQ/migration_backups_20260625/arka_hq_phase19_travel_mode_status_stable_20260625.bundle",
        smoke_stack_passed=False,
    )

    blocked_data = blocked.to_dict()

    print("")
    print("BLOCKED RELEASE CANDIDATE STATUS DICT:")
    print(blocked_data)

    assert blocked_data["release_decision"] == "release_candidate_blocked", blocked_data
    assert blocked_data["smoke_stack_passed"] is False, blocked_data
    assert "Resolve failed smoke evidence" in blocked_data["next_safe_action"], blocked_data
    check_safe_metadata(blocked_data["metadata"])

    print("")
    print("[OK] Phase 20 release candidate status smoke proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
