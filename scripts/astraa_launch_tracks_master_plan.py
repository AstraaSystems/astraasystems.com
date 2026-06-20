#!/usr/bin/env python3
"""
Astraa Launch Tracks Master Plan

READ-ONLY SCRIPT.

Purpose:
- Coordinate the three launch tracks:
  A) public website QA
  B) production auth provider/session path
  C) managed DB staging setup
- Provide a clear launch decision view.

Does NOT:
- modify files
- deploy Astraa
- connect to databases
- change auth behavior
- migrate data
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ("Public website QA checklist", [sys.executable, "scripts/astraa_public_website_qa_checklist.py"]),
    ("Auth provider decision matrix", [sys.executable, "scripts/astraa_auth_provider_decision_matrix.py"]),
    ("Managed DB staging setup decision", [sys.executable, "scripts/astraa_managed_db_staging_setup_decision.py"]),
    ("Public launch readiness master checklist", [sys.executable, "scripts/astraa_public_launch_readiness_master_checklist.py"]),
    ("Managed DB readiness proof", [sys.executable, "scripts/astraa_managed_db_readiness_proof.py"]),
    ("Production auth readiness proof", [sys.executable, "scripts/astraa_production_auth_readiness_proof.py"]),
    ("CORS hardening proof", [sys.executable, "scripts/astraa_cors_hardening_proof.py"]),
    ("Post-auth-hardening proof", [sys.executable, "scripts/astraa_post_auth_hardening_proof.py"]),
    ("Gunicorn local smoke test", [sys.executable, "scripts/astraa_gunicorn_local_smoke_test.py"]),
    ("Staging pipeline proof", [sys.executable, "scripts/astraa_staging_pipeline_proof.py"]),
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
    section("ASTRAA LAUNCH TRACKS MASTER PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", ROOT)

    results = {}

    for name, cmd in COMMANDS:
        results[name] = run(name, cmd)

    section("LAUNCH TRACK SUMMARY")

    all_ok = True
    for name, code in results.items():
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status}: {name} ({code})")
        if code != 0:
            all_ok = False

    print("")
    if all_ok:
        print("✅ LAUNCH TRACKS MASTER PLAN PASSED")
        print("Marketing/public website QA can proceed as the next practical launch step.")
        print("Paid customer SaaS launch remains blocked until production auth, managed DB, deployed secrets, host/TLS, and live deployed Moneris regression are complete.")
    else:
        print("❌ LAUNCH TRACKS MASTER PLAN FAILED")
        print("Review failed sections above before moving forward.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify files.")
    print("This script did not deploy Astraa.")
    print("This script did not connect to databases.")
    print("This script did not change auth behavior.")
    print("This script did not migrate data.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
