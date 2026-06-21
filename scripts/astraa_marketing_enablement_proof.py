#!/usr/bin/env python3
"""
Astraa Marketing Enablement Proof

DEFAULT-SAFE SCRIPT.

Purpose:
- Verify Astraa marketing enablement files and public website QA after metadata/copy updates.

Does NOT:
- send marketing messages
- post to social media
- deploy Astraa
- change backend/auth/payment behavior
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ("Marketing enablement plan", [sys.executable, "scripts/astraa_marketing_enablement_plan.py"]),
    ("Marketing copy library", [sys.executable, "scripts/astraa_marketing_copy_library.py"]),
    ("Public website risk classifier", [sys.executable, "scripts/astraa_public_website_risk_classifier.py"]),
    ("Public website file inventory", [sys.executable, "scripts/astraa_public_website_file_inventory.py"]),
    ("Paid SaaS blocker execution plan", [sys.executable, "scripts/astraa_paid_saas_blocker_execution_plan.py"]),
    ("Paid SaaS implementation lane", [sys.executable, "scripts/astraa_paid_saas_implementation_lane.py"]),
    ("Production auth provider selection decision", [sys.executable, "scripts/astraa_production_auth_provider_selection_decision.py"]),
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
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)

    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print("\nSTDERR:")
        print(proc.stderr.rstrip())

    print("\nExit code:", proc.returncode)
    return proc.returncode


def main():
    section("ASTRAA MARKETING ENABLEMENT PROOF")
    print("Mode: DEFAULT-SAFE")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    results = {}
    for name, cmd in COMMANDS:
        results[name] = run(name, cmd)

    section("MARKETING ENABLEMENT SUMMARY")
    all_ok = True
    for name, code in results.items():
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status}: {name} ({code})")
        if code != 0:
            all_ok = False

    print("")
    if all_ok:
        print("✅ ASTRAA MARKETING ENABLEMENT PROOF PASSED")
    else:
        print("❌ ASTRAA MARKETING ENABLEMENT PROOF FAILED")

    section("SAFETY CONFIRMATION")
    print("This script did not send marketing messages.")
    print("This script did not post to social media.")
    print("This script did not deploy Astraa.")
    print("This script did not change backend/auth/payment behavior.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
