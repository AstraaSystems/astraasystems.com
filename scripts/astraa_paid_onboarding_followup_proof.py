#!/usr/bin/env python3
"""
Astraa Paid Onboarding Follow-Up Proof

READ-ONLY SCRIPT.

Purpose:
- Run paid onboarding follow-up planning scripts.
- Confirm customer follow-up process exists without sending messages or storing real customer data.

Does NOT:
- send emails
- create drafts
- schedule meetings
- open customer access
- store customer data
- modify backend/auth/payment behavior
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ("Paid onboarding follow-up process", [sys.executable, "scripts/astraa_paid_onboarding_followup_process.py"]),
    ("Paid onboarding response templates", [sys.executable, "scripts/astraa_paid_onboarding_response_templates.py"]),
    ("Paid onboarding tracker template", [sys.executable, "scripts/astraa_paid_onboarding_followup_tracker_template.py"]),
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
    section("ASTRAA PAID ONBOARDING FOLLOW-UP PROOF")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    results = {}
    for name, cmd in COMMANDS:
        results[name] = run(name, cmd)

    section("SUMMARY")
    all_ok = True
    for name, code in results.items():
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status}: {name} ({code})")
        if code != 0:
            all_ok = False

    print("")
    if all_ok:
        print("✅ PAID ONBOARDING FOLLOW-UP PROOF PASSED")
    else:
        print("❌ PAID ONBOARDING FOLLOW-UP PROOF FAILED")

    section("READ-ONLY CONFIRMATION")
    print("This script did not send emails.")
    print("This script did not create drafts.")
    print("This script did not schedule meetings.")
    print("This script did not open customer access.")
    print("This script did not store customer data.")
    print("This script did not modify backend/auth/payment behavior.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
