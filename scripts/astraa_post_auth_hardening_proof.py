#!/usr/bin/env python3
"""
Astraa Post-Auth-Hardening Proof

DEFAULT-SAFE LOCAL RUNTIME ORCHESTRATION SCRIPT.

Purpose:
- Prove post-auth-hardening behavior in one command:
  1. api.py syntax check
  2. auth acceptance test syntax check
  3. staging pipeline proof
  4. auth acceptance block mode
  5. auth acceptance override mode
  6. git status/log summary

Does NOT:
- modify source files
- create users
- create production sessions
- migrate data
- modify JSON/JSONL source files

Notes:
- This script starts and stops local api.py subprocesses.
- It uses public-launch mode.
- It intentionally unsets/sets ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE for block/override proofs.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def run_command(name, cmd, env=None):
    section(name)
    print("Command:", " ".join(cmd))

    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env or os.environ.copy(),
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


def base_env():
    env = os.environ.copy()
    env["ASTRAA_STORAGE_BACKEND"] = "json"
    env["ASTRAA_PUBLIC_LAUNCH_MODE"] = "true"
    env["ASTRAA_REQUEST_GUARD_ENABLED"] = "true"

    # Keep unrelated staging mutation flags off for proof safety.
    env.pop("ASTRAA_ALLOW_STAGING_IMPORT", None)
    env.pop("ASTRAA_ALLOW_STAGING_DB_CREATE", None)

    return env


def stop_port_5000():
    subprocess.run(
        ["bash", "-lc", "fuser -k 5000/tcp 2>/dev/null || true"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )


def start_api(env):
    stop_port_5000()

    proc = subprocess.Popen(
        [sys.executable, "api.py"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Give server a short startup window.
    time.sleep(2)

    if proc.poll() is not None:
        output = ""
        if proc.stdout:
            output = proc.stdout.read()
        raise RuntimeError(f"api.py exited during startup. Output:\n{output}")

    return proc


def stop_api(proc):
    if proc.poll() is not None:
        return

    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def run_auth_acceptance_mode(name, allow_dev_login):
    section(name)

    env = base_env()

    if allow_dev_login:
        env["ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE"] = "true"
    else:
        env.pop("ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE", None)

    proc = None

    try:
        proc = start_api(env)

        result = subprocess.run(
            [sys.executable, "scripts/astraa_auth_acceptance_tests.py"],
            cwd=str(ROOT),
            env=env,
            text=True,
            capture_output=True,
        )

        if result.stdout:
            print(result.stdout.rstrip())

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr.rstrip())

        print("\nExit code:", result.returncode)
        return result.returncode
    finally:
        if proc is not None:
            stop_api(proc)
        stop_port_5000()


def main():
    section("ASTRAA POST-AUTH-HARDENING PROOF")
    print("Mode: DEFAULT-SAFE LOCAL RUNTIME PROOF")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", ROOT)

    results = {}

    results["api_py_compile"] = run_command(
        "1. api.py syntax check",
        [sys.executable, "-m", "py_compile", "api.py"],
    )

    results["auth_test_py_compile"] = run_command(
        "2. auth acceptance test syntax check",
        [sys.executable, "-m", "py_compile", "scripts/astraa_auth_acceptance_tests.py"],
    )

    results["staging_pipeline_proof"] = run_command(
        "3. staging pipeline proof",
        [sys.executable, "scripts/astraa_staging_pipeline_proof.py"],
        env=base_env(),
    )

    results["auth_block_mode"] = run_auth_acceptance_mode(
        "4. auth acceptance block mode",
        allow_dev_login=False,
    )

    results["auth_override_mode"] = run_auth_acceptance_mode(
        "5. auth acceptance override mode",
        allow_dev_login=True,
    )

    results["git_status"] = run_command(
        "6. git status",
        ["git", "status", "-sb"],
    )

    results["git_log"] = run_command(
        "7. git log",
        ["git", "log", "--oneline", "-n", "12"],
    )

    section("POST-AUTH-HARDENING PROOF SUMMARY")

    all_ok = True

    for name, code in results.items():
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status}: {name} ({code})")
        if code != 0:
            all_ok = False

    print("")

    if all_ok:
        print("✅ POST-AUTH-HARDENING PROOF PASSED")
    else:
        print("❌ POST-AUTH-HARDENING PROOF FAILED")

    section("SAFETY CONFIRMATION")
    print("This script did not modify source files.")
    print("This script did not create users.")
    print("This script did not create production sessions.")
    print("This script did not migrate data.")
    print("This script did not modify JSON/JSONL source files.")
    print("This script stopped local api.py processes it started.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
