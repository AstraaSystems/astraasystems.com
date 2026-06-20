#!/usr/bin/env python3
"""
Astraa Gunicorn Local Smoke Test

LOCAL RUNTIME TEST SCRIPT.

Purpose:
- Start Astraa through Gunicorn locally using wsgi:app.
- Verify /health.
- Verify allowed-origin CORS header.
- Stop Gunicorn after test.

Does NOT:
- create services
- create nginx configs
- deploy Astraa
- modify source files
- migrate data
- modify JSON/JSONL source files
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:5000"
ALLOWED_ORIGIN = "https://astraasystems.com"


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def stop_port_5000():
    subprocess.run(
        ["bash", "-lc", "fuser -k 5000/tcp 2>/dev/null || true"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )


def proof_env():
    env = os.environ.copy()
    env["ASTRAA_STORAGE_BACKEND"] = "json"
    env["ASTRAA_PUBLIC_LAUNCH_MODE"] = "true"
    env["ASTRAA_REQUEST_GUARD_ENABLED"] = "true"
    env["ASTRAA_ALLOWED_ORIGINS"] = "https://astraasystems.com,https://www.astraasystems.com"
    env["ASTRAA_ALLOW_LOCALHOST_CORS"] = "true"
    env["ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE"] = "true"

    env.pop("ASTRAA_ALLOW_STAGING_IMPORT", None)
    env.pop("ASTRAA_ALLOW_STAGING_DB_CREATE", None)

    return env


def request_health():
    req = urllib.request.Request(
        BASE_URL + "/health",
        headers={"Origin": ALLOWED_ORIGIN},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            headers = dict(resp.headers)
            return resp.status, headers, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers), body
    except Exception as exc:
        return 0, {}, str(exc)


def main():
    section("ASTRAA GUNICORN LOCAL SMOKE TEST")
    print("Mode: LOCAL RUNTIME TEST")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Repository root:", ROOT)

    gunicorn_path = shutil.which("gunicorn")

    if not gunicorn_path:
        section("GUNICORN NOT INSTALLED")
        print("gunicorn command was not found in PATH.")
        print("No service was started.")
        print("Install gunicorn in the virtual environment before running this smoke test.")
        print("")
        print("Suggested local install command when ready:")
        print("pip install gunicorn")
        section("READ-ONLY CONFIRMATION")
        print("This script did not modify files.")
        print("This script did not start services.")
        print("This script did not deploy Astraa.")
        raise SystemExit(0)

    section("STARTING GUNICORN")
    print("Gunicorn path:", gunicorn_path)

    stop_port_5000()

    cmd = [
        gunicorn_path,
        "--bind", "127.0.0.1:5000",
        "--workers", "2",
        "--threads", "2",
        "--timeout", "120",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "wsgi:app",
    ]

    print("Command:", " ".join(cmd))

    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        env=proof_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        time.sleep(3)

        if proc.poll() is not None:
            output = proc.stdout.read() if proc.stdout else ""
            section("GUNICORN FAILED TO START")
            print(output)
            raise SystemExit(1)

        section("HEALTH CHECK")
        status, headers, body = request_health()
        acao = None
        for key, value in headers.items():
            if key.lower() == "access-control-allow-origin":
                acao = value

        print("Status:", status)
        print("Access-Control-Allow-Origin:", acao)
        print("Body preview:", body[:300])

        ok = status == 200 and acao == ALLOWED_ORIGIN

        section("SMOKE TEST SUMMARY")
        if ok:
            print("✅ GUNICORN LOCAL SMOKE TEST PASSED")
        else:
            print("❌ GUNICORN LOCAL SMOKE TEST FAILED")
            raise SystemExit(1)

    finally:
        section("STOPPING GUNICORN")
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

        stop_port_5000()

    section("READ-ONLY CONFIRMATION")
    print("This script did not create services.")
    print("This script did not create nginx configs.")
    print("This script did not deploy Astraa.")
    print("This script did not modify source files.")
    print("This script did not migrate data.")
    print("This script stopped the local Gunicorn process it started.")


if __name__ == "__main__":
    main()
