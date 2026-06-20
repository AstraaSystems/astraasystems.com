#!/usr/bin/env python3
"""
Astraa Staging Pipeline Proof

READ-ONLY / DEFAULT-SAFE ORCHESTRATION SCRIPT.

Purpose:
- Prove the local staging DB pipeline is healthy.
- Run validation, row inspection, reconciliation, and guarded refusal checks.
- Confirm git status/log summary.

Does NOT:
- create a database
- create tables
- create indexes
- insert records
- update records
- delete records
- migrate data
- modify JSON/JSONL source files

Important:
- This script intentionally clears ASTRAA_ALLOW_STAGING_DB_CREATE and
  ASTRAA_ALLOW_STAGING_IMPORT for its child processes to prove default refusal mode.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


COMMANDS = [
    {
        "name": "Staging DB validation",
        "cmd": [sys.executable, "scripts/astraa_staging_db_validate.py"],
        "required": True,
    },
    {
        "name": "Staging DB row inspector",
        "cmd": [sys.executable, "scripts/astraa_staging_db_row_inspector.py"],
        "required": True,
    },
    {
        "name": "Staging DB reconciliation",
        "cmd": [sys.executable, "scripts/astraa_staging_db_reconcile.py"],
        "required": True,
    },
    {
        "name": "Guarded staging DB create template should refuse by default",
        "cmd": [sys.executable, "scripts/astraa_staging_db_create_template.py"],
        "required": True,
        "must_contain": "Refusing to create staging DB because ASTRAA_ALLOW_STAGING_DB_CREATE is not true.",
    },
    {
        "name": "Guarded staging import should refuse by default",
        "cmd": [sys.executable, "scripts/astraa_staging_import_guarded.py"],
        "required": True,
        "must_contain": "Refusing to import because ASTRAA_ALLOW_STAGING_IMPORT is not true.",
    },
    {
        "name": "Git status",
        "cmd": ["git", "status", "-sb"],
        "required": True,
    },
    {
        "name": "Git log",
        "cmd": ["git", "log", "--oneline", "-n", "12"],
        "required": True,
    },
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def safe_child_env():
    env = os.environ.copy()

    # Force refusal/default-safe mode for proof.
    env.pop("ASTRAA_ALLOW_STAGING_DB_CREATE", None)
    env.pop("ASTRAA_ALLOW_STAGING_IMPORT", None)

    # Keep engine/path if user has them set, but no creation/import can occur without flags.
    env.setdefault("ASTRAA_STAGING_DB_ENGINE", "sqlite")

    return env


def run_command(item):
    section(item["name"])
    print("Command:", " ".join(item["cmd"]))

    proc = subprocess.run(
        item["cmd"],
        cwd=str(ROOT),
        env=safe_child_env(),
        text=True,
        capture_output=True,
    )

    if proc.stdout:
        print(proc.stdout.rstrip())

    if proc.stderr:
        print("\nSTDERR:")
        print(proc.stderr.rstrip())

    print("\nExit code:", proc.returncode)

    ok = proc.returncode == 0

    must_contain = item.get("must_contain")
    if must_contain:
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        if must_contain not in combined:
            ok = False
            print("\n❌ Expected refusal text not found:")
            print(must_contain)
        else:
            print("\n✅ Expected refusal text found.")

    return ok


def main():
    section("ASTRAA STAGING PIPELINE PROOF")
    print("Mode: READ ONLY / DEFAULT-SAFE")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", ROOT)

    results = []

    for item in COMMANDS:
        ok = run_command(item)
        results.append((item["name"], ok, item.get("required", False)))

    section("STAGING PIPELINE PROOF SUMMARY")

    all_required_ok = True

    for name, ok, required in results:
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {name}")

        if required and not ok:
            all_required_ok = False

    print("")
    if all_required_ok:
        print("✅ STAGING PIPELINE PROOF PASSED")
        print("Validation, inspection, reconciliation, and guarded refusal checks completed successfully.")
    else:
        print("❌ STAGING PIPELINE PROOF FAILED")
        print("Review failed sections above before continuing.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not create a database.")
    print("This script did not create tables.")
    print("This script did not create indexes.")
    print("This script did not insert records.")
    print("This script did not update records.")
    print("This script did not delete records.")
    print("This script did not migrate data.")
    print("This script did not modify JSON/JSONL source files.")
    print("Child processes were run with staging create/import flags unset.")

    raise SystemExit(0 if all_required_ok else 1)


if __name__ == "__main__":
    main()
