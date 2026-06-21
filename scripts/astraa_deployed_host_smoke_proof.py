#!/usr/bin/env python3
"""
Astraa Deployed Host Smoke Proof

READ-ONLY SCRIPT.

Purpose:
- Provide a guarded smoke proof for final deployed Host/TLS readiness.
- Verify only after a final deployed HTTPS base URL is available.
- Keep deployed host smoke proof separate from deployed Moneris regression.

Does NOT:
- deploy Astraa
- start services
- modify Nginx/systemd
- request TLS certificates
- print secrets
- change backend/auth/payment behavior
- unlock customer access
- run Moneris payments

Usage:
    ASTRAA_DEPLOYED_BASE_URL=https://app.example.com python3 scripts/astraa_deployed_host_smoke_proof.py

Optional:
    ASTRAA_DEPLOYED_HEALTH_PATH=/health
"""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse


def section(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def pass_line(message: str) -> None:
    print("[PASS]", message)


def fail_line(message: str) -> None:
    print("[FAIL]", message)


def warn_line(message: str) -> None:
    print("[WARN]", message)


def read_url(url: str, timeout: int = 15) -> tuple[int | None, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Astraa-Deployed-Host-Smoke-Proof/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(2048).decode("utf-8", errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", errors="replace")
        return exc.code, body
    except Exception as exc:
        return None, repr(exc)


def main() -> int:
    failures: list[str] = []

    section("ASTRAA DEPLOYED HOST SMOKE PROOF")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    base_url = os.environ.get("ASTRAA_DEPLOYED_BASE_URL", "").strip()
    health_path = os.environ.get("ASTRAA_DEPLOYED_HEALTH_PATH", "/health").strip() or "/health"

    section("CONFIGURATION")
    if not base_url:
        warn_line("ASTRAA_DEPLOYED_BASE_URL is not set.")
        warn_line("No deployed host smoke check was performed.")
        warn_line("Set ASTRAA_DEPLOYED_BASE_URL only after final host/subdomain is chosen.")
        print("Result: SKIPPED")
        return 0

    print("ASTRAA_DEPLOYED_BASE_URL:", base_url)
    print("ASTRAA_DEPLOYED_HEALTH_PATH:", health_path)

    parsed = urlparse(base_url)

    section("HOST/TLS URL CHECK")
    if parsed.scheme == "https":
        pass_line("Base URL uses HTTPS.")
    else:
        failures.append("Base URL must use HTTPS.")
        fail_line("Base URL must use HTTPS.")

    if parsed.netloc:
        pass_line("Base URL includes a host.")
    else:
        failures.append("Base URL is missing host.")
        fail_line("Base URL is missing host.")

    if "*" in base_url:
        failures.append("Base URL must not contain wildcard.")
        fail_line("Base URL must not contain wildcard.")
    else:
        pass_line("Base URL does not contain wildcard.")

    section("HEALTH ENDPOINT CHECK")
    health_url = base_url.rstrip("/") + "/" + health_path.lstrip("/")
    print("Health URL:", health_url)

    if parsed.scheme == "https" and parsed.netloc:
        status, body = read_url(health_url)

        if status is None:
            failures.append(f"Health endpoint request failed: {body}")
            fail_line(f"Health endpoint request failed: {body}")
        elif 200 <= status < 300:
            pass_line(f"Health endpoint responded with HTTP {status}.")
            print("Response preview:", body[:300].replace("\n", " "))
        else:
            failures.append(f"Health endpoint must return HTTP 2xx, got HTTP {status}")
            fail_line(f"Health endpoint must return HTTP 2xx, got HTTP {status}")
            print("Response preview:", body[:300].replace("\n", " "))
    else:
        warn_line("Skipped health request because base URL failed URL validation.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not deploy Astraa.")
    print("This script did not start services.")
    print("This script did not modify Nginx/systemd.")
    print("This script did not request TLS certificates.")
    print("This script did not print secrets.")
    print("This script did not change backend/auth/payment behavior.")
    print("This script did not unlock customer access.")
    print("This script did not run Moneris payments.")

    section("RESULT")
    if failures:
        print("DEPLOYED HOST SMOKE PROOF: FAIL")
        print("Failures:")
        for failure in failures:
            print("-", failure)
        return 1

    print("DEPLOYED HOST SMOKE PROOF: PASS")
    print("Deployed HTTPS API health endpoint responded successfully over TLS.")
    print("Next blocker after deployed Host/TLS smoke proof: deployed CORS smoke proof.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
