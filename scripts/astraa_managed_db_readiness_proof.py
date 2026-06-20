#!/usr/bin/env python3
"""
Astraa Managed DB Readiness Proof

DEFAULT-SAFE READINESS ORCHESTRATION SCRIPT.

Purpose:
- Run managed DB planning scripts and existing local staging proof.
- Confirm managed DB work remains planning-only until provider/cutover is chosen.

Does NOT:
- connect to a managed database
- create databases
- migrate data
- modify api.py
- patch runtime behavior
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ("Managed DB provider plan", [sys.executable, "scripts/astraa_managed_db_provider_plan.py"]),
    ("Managed DB requirements", [sys.executable, "scripts/astraa_managed_db_requirements.py"]),
    ("Managed DB cutover plan", [sys.executable, "scripts/astraa_managed_db_cutover_plan.py"]),
    ("Local staging pipeline proof", [sys.executable, "scripts/astraa_staging_pipeline_proof.py"]),
    ("Post-auth-hardening proof", [sys.executable, "scripts/astraa_post_auth_hardening_proof.py"]),
    ("CORS hardening proof", [sys.executable, "scripts/astraa_cors_hardening_proof.py"]),
    ("Gunicorn local smoke test", [sys.executable, "scripts/astraa_gunicorn_local_smoke_test.py"]),
    ("Git status", ["git", "status", "-sb"]),
    ("Git log", ["git", "log", "--oneline", "-n", "12"]),
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def run(name, cmd):
    section(name)
    print("Command:", " ".join(cmd))

    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    if proc.stdout:
        print(proc.stdout.rstrip())

    if proc.stderr:
        print("\nSTDERR:")
        print(proc.stderr.rstrip())

    print("\nExit code:", proc.returncode)
    return proc.returncode


def main():
    section("ASTRAA MANAGED DB READINESS PROOF")
    print("Mode: DEFAULT-SAFE / NO DB CONNECTION")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", ROOT)

    results = {}

    for name, cmd in COMMANDS:
        results[name] = run(name, cmd)

    section("MANAGED DB READINESS SUMMARY")

    all_ok = True
    for name, code in results.items():
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status}: {name} ({code})")
        if code != 0:
            all_ok = False

    print("")
    if all_ok:
        print("✅ MANAGED DB READINESS PROOF PASSED")
    else:
        print("❌ MANAGED DB READINESS PROOF FAILED")

    section("READ-ONLY / SAFETY CONFIRMATION")
    print("This script did not connect to a managed database.")
    print("This script did not create databases.")
    print("This script did not migrate data.")
    print("This script did not modify api.py.")
    print("This script did not patch runtime behavior.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
