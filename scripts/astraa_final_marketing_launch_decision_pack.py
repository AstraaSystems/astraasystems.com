#!/usr/bin/env python3
"""
Astraa Final Marketing Launch Decision Pack

DEFAULT-SAFE SCRIPT.

Purpose:
- Run final marketing launch go/no-go checklist.
- Summarize paid SaaS blockers.
- Print announcement copy.
- Re-run website and marketing readiness checks.

Does NOT:
- deploy Astraa
- send marketing messages
- post to social media
- open customer access
- change backend/auth/payment behavior
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ("Final marketing launch go/no-go", [sys.executable, "scripts/astraa_final_marketing_launch_go_no_go.py"]),
    ("Paid SaaS blockers summary", [sys.executable, "scripts/astraa_paid_saas_blockers_summary.py"]),
    ("Marketing launch announcement copy", [sys.executable, "scripts/astraa_marketing_launch_announcement_copy.py"]),
    ("Marketing browser QA checklist", [sys.executable, "scripts/astraa_marketing_browser_qa_checklist.py"]),
    ("Marketing enablement proof", [sys.executable, "scripts/astraa_marketing_enablement_proof.py"]),
    ("Public website risk classifier", [sys.executable, "scripts/astraa_public_website_risk_classifier.py"]),
    ("Public website file inventory", [sys.executable, "scripts/astraa_public_website_file_inventory.py"]),
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
    section("ASTRAA FINAL MARKETING LAUNCH DECISION PACK")
    print("Mode: DEFAULT-SAFE")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    results = {}

    for name, cmd in COMMANDS:
        results[name] = run(name, cmd)

    section("FINAL DECISION PACK SUMMARY")

    all_ok = True

    for name, code in results.items():
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status}: {name} ({code})")
        if code != 0:
            all_ok = False

    print("")

    if all_ok:
        print("✅ FINAL MARKETING LAUNCH DECISION PACK PASSED")
        print("Marketing/public website visibility can proceed after human browser visual review.")
        print("Paid SaaS onboarding remains blocked until production auth, managed DB, deployment secrets, host/TLS, and deployed Moneris regression are complete.")
    else:
        print("❌ FINAL MARKETING LAUNCH DECISION PACK FAILED")

    section("SAFETY CONFIRMATION")
    print("This script did not deploy Astraa.")
    print("This script did not send marketing messages.")
    print("This script did not post to social media.")
    print("This script did not open customer access.")
    print("This script did not change backend/auth/payment behavior.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
