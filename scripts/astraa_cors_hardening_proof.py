#!/usr/bin/env python3
"""
Astraa CORS Hardening Proof

DEFAULT-SAFE LOCAL RUNTIME ORCHESTRATION SCRIPT.

Purpose:
- Prove CORS/domain lock behavior in one command:
  1. api.py syntax check
  2. CORS acceptance test syntax check
  3. Start local api.py with strict CORS/public-launch env
  4. Run CORS acceptance tests
  5. Run auth/preload/payment allowed-origin regression
  6. Run post-auth-hardening proof
  7. Print git status/log

Does NOT:
- modify source files
- create users
- create production sessions
- migrate data
- modify JSON/JSONL source files

Notes:
- This script starts and stops local api.py subprocesses.
- It uses public-launch mode.
- It allows localhost CORS only for internal QA proof.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://localhost:5000"
ALLOWED_ORIGIN = "https://astraasystems.com"


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


def proof_env():
    env = os.environ.copy()
    env["ASTRAA_STORAGE_BACKEND"] = "json"
    env["ASTRAA_PUBLIC_LAUNCH_MODE"] = "true"
    env["ASTRAA_REQUEST_GUARD_ENABLED"] = "true"
    env["ASTRAA_ALLOWED_ORIGINS"] = "https://astraasystems.com,https://www.astraasystems.com"
    env["ASTRAA_ALLOW_LOCALHOST_CORS"] = "true"
    env["ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE"] = "true"

    # Keep staging mutation flags off.
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


def request_json(path, method="GET", payload=None, token=None, origin=ALLOWED_ORIGIN):
    headers = {
        "Origin": origin,
    }

    data = None

    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        BASE_URL + path,
        headers=headers,
        data=data,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
            return resp.status, dict(resp.headers), parsed
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return exc.code, dict(exc.headers), parsed
    except Exception as exc:
        return 0, {}, {"error": str(exc)}


def check(condition, label, details=None):
    if condition:
        print(f"PASS: {label}")
        return True

    print(f"FAIL: {label}")
    if details is not None:
        print(json.dumps(details, indent=2, sort_keys=True))
    return False


def allowed_origin_regression():
    section("Allowed-origin auth/preload/payment regression")

    results = []

    login_status, login_headers, login_body = request_json(
        "/api/auth/dev-login",
        method="POST",
        payload={
            "account_email": "approved.live.test@astraasystems.com",
            "selected_plan": "Professional",
        },
    )

    token = login_body.get("token")

    results.append(check(
        login_status == 200 and login_body.get("status") == "ok" and bool(token),
        "Allowed-origin dev-login returns token with internal QA override",
        {"status": login_status, "body": login_body},
    ))

    if not token:
        return 1

    me_status, me_headers, me_body = request_json(
        "/api/auth/me",
        method="GET",
        token=token,
    )

    results.append(check(
        me_status == 200 and me_body.get("status") == "ok",
        "Allowed-origin auth/me returns status ok",
        {"status": me_status, "body": me_body},
    ))

    preload_status, preload_headers, preload_body = request_json(
        "/preload",
        method="POST",
        payload={
            "email": "approved.live.test@astraasystems.com",
            "checkout_email": "approved.live.test@astraasystems.com",
            "tool": "Astraa Estimator",
            "selected_tool": "Astraa Estimator",
            "plan": "professional",
            "selected_plan": "Professional",
            "price": "$99.99 CAD/month",
            "amount": "2.00",
        },
    )

    results.append(check(
        preload_status == 200
        and preload_body.get("status") == "ok"
        and preload_body.get("success") is True,
        "Allowed-origin preload returns success true",
        {"status": preload_status, "body": preload_body},
    ))

    verify_status, verify_headers, verify_body = request_json(
        "/api/payment/verify-moneris-receipt",
        method="POST",
        token=token,
        payload={
            "account_email": "malicious-change@example.com",
            "selected_tool": "Astraa Estimator",
            "selected_plan": "Professional",
            "purchase_type": "subscription_professional",
            "moneris_ticket": "1781891159jSb8V8UZyDDY8VydC1cQ8GtwQGu0OT",
        },
    )

    payment = verify_body.get("payment") or {}

    results.append(check(
        verify_status == 200
        and verify_body.get("status") == "ok"
        and verify_body.get("payment_verified") is True
        and payment.get("account_email") == "approved.live.test@astraasystems.com",
        "Allowed-origin payment verification replay uses authorized account",
        {"status": verify_status, "body": verify_body},
    ))

    return 0 if all(results) else 1


def main():
    section("ASTRAA CORS HARDENING PROOF")
    print("Mode: DEFAULT-SAFE LOCAL RUNTIME PROOF")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Working directory:", ROOT)

    env = proof_env()
    results = {}

    results["api_py_compile"] = run_command(
        "1. api.py syntax check",
        [sys.executable, "-m", "py_compile", "api.py"],
    )

    results["cors_test_py_compile"] = run_command(
        "2. CORS acceptance test syntax check",
        [sys.executable, "-m", "py_compile", "scripts/astraa_cors_acceptance_tests.py"],
    )

    proc = None

    try:
        section("3. Start api.py for CORS proof")
        proc = start_api(env)
        print("api.py started for CORS proof.")

        results["cors_acceptance_tests"] = run_command(
            "4. CORS acceptance tests",
            [sys.executable, "scripts/astraa_cors_acceptance_tests.py"],
            env=env,
        )

        results["allowed_origin_regression"] = allowed_origin_regression()

    finally:
        if proc is not None:
            stop_api(proc)
        stop_port_5000()

    results["post_auth_hardening_proof"] = run_command(
        "6. Post-auth-hardening proof",
        [sys.executable, "scripts/astraa_post_auth_hardening_proof.py"],
        env=env,
    )

    results["git_status"] = run_command(
        "7. git status",
        ["git", "status", "-sb"],
    )

    results["git_log"] = run_command(
        "8. git log",
        ["git", "log", "--oneline", "-n", "12"],
    )

    section("CORS HARDENING PROOF SUMMARY")

    all_ok = True

    for name, code in results.items():
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status}: {name} ({code})")
        if code != 0:
            all_ok = False

    print("")

    if all_ok:
        print("✅ CORS HARDENING PROOF PASSED")
    else:
        print("❌ CORS HARDENING PROOF FAILED")

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
