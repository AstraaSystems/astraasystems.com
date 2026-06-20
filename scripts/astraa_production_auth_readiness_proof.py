#!/usr/bin/env python3
"""
Astraa Production Auth Readiness Proof

DEFAULT-SAFE ORCHESTRATION SCRIPT.

Purpose:
- Prove the production-auth planning foundation is complete.
- Run auth planning/readiness scripts plus existing runtime proof suites.

Does NOT:
- modify api.py
- change auth behavior
- create users
- create sessions
- connect to an auth provider
- deploy Astraa
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


COMMANDS = [
    ("Production auth provider plan", [sys.executable, "scripts/astraa_production_auth_provider_plan.py"]),
    ("Production auth provider inventory", [sys.executable, "scripts/astraa_production_auth_provider_inventory.py"]),
    ("Production auth acceptance skeleton", [sys.executable, "scripts/astraa_production_auth_acceptance_skeleton.py"]),
    ("Production auth identity contract", [sys.executable, "scripts/astraa_production_auth_identity_contract.py"]),
    ("Production identity resolver interface plan", [sys.executable, "scripts/astraa_production_identity_resolver_interface_plan.py"]),
    ("Production auth mode flag plan", [sys.executable, "scripts/astraa_production_auth_mode_flag_plan.py"]),
    ("Production auth mode acceptance skeleton", [sys.executable, "scripts/astraa_production_auth_mode_acceptance_skeleton.py"]),
    ("Post-auth-hardening proof", [sys.executable, "scripts/astraa_post_auth_hardening_proof.py"]),
    ("CORS hardening proof", [sys.executable, "scripts/astraa_cors_hardening_proof.py"]),
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
    section("ASTRAA PRODUCTION AUTH READINESS PROOF")
    print("Mode: DEFAULT-SAFE")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", ROOT)

    results = {}

    for name, cmd in COMMANDS:
        results[name] = run(name, cmd)

    section("PRODUCTION AUTH READINESS SUMMARY")

    all_ok = True

    for name, code in results.items():
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status}: {name} ({code})")

        if code != 0:
            all_ok = False

    print("")

    if all_ok:
        print("✅ PRODUCTION AUTH READINESS PROOF PASSED")
    else:
        print("❌ PRODUCTION AUTH READINESS PROOF FAILED")

    section("READ-ONLY / SAFETY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not change auth behavior.")
    print("This script did not create users or sessions.")
    print("This script did not connect to an auth provider.")
    print("This script did not deploy Astraa.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
