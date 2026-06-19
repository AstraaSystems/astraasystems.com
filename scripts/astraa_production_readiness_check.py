#!/usr/bin/env python3
"""
Astraa Production Readiness Check

READ-ONLY ORCHESTRATION SCRIPT.
Runs existing read-only scripts and prints a checkpoint summary.

Does not delete, modify, archive, migrate, repair, or commit files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "scripts/astraa_storage_backend_selftest.py",
    "scripts/astraa_audit_runtime_data.py",
    "scripts/astraa_plan_runtime_cleanup.py",
    "scripts/astraa_storage_inventory.py",
    "scripts/astraa_route_function_inventory.py",
    "scripts/astraa_active_function_map.py",
]


def run_command(label, cmd):
    print("\n" + "=" * 100)
    print(label)
    print("=" * 100)
    print("Command:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    print("Exit code:", result.returncode)

    return result.returncode


def main():
    print("=" * 100)
    print("ASTRAA PRODUCTION READINESS CHECK")
    print("=" * 100)
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", ROOT)

    exit_codes = []

    for script in SCRIPTS:
        script_path = ROOT / script

        if not script_path.exists():
            print("\nMISSING SCRIPT:", script)
            exit_codes.append(1)
            continue

        exit_codes.append(run_command(script, [sys.executable, script]))

    exit_codes.append(run_command("git status -sb", ["git", "status", "-sb"]))
    exit_codes.append(run_command("git log --oneline -n 12", ["git", "log", "--oneline", "-n", "12"]))

    print("\n" + "=" * 100)
    print("READINESS CHECK SUMMARY")
    print("=" * 100)

    failed = [code for code in exit_codes if code != 0]

    if failed:
        print("Status: ATTENTION NEEDED")
        print("One or more read-only checks returned a non-zero exit code.")
        sys.exit(1)

    print("Status: READ-ONLY CHECKS PASSED")
    print("No files were intentionally modified by this orchestration script.")
    print("This does not mean full public production launch is complete; it means the local hardening checks ran successfully.")


if __name__ == "__main__":
    main()
