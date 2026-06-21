#!/usr/bin/env python3
"""
Astraa Deployed CORS Smoke Proof

READ-ONLY SCRIPT.

Purpose:
- Provide a guarded deployed CORS smoke proof for final Host/TLS readiness.
- Verify CORS behavior only after a final deployed HTTPS base URL is available.
- Keep deployed CORS proof separate from deployed Moneris regression.

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
    ASTRAA_DEPLOYED_BASE_URL=https://app.example.com \
    ASTRAA_CORS_TEST_ORIGIN=https://www.example.com \
    python3 scripts/astraa_deployed_cors_smoke_proof.py

Optional:
    ASTRAA_CORS_TEST_PATH=/health
"""

from __future__ import annotations

import os
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


def request_with_origin(url: str, origin: str, timeout: int = 15) -> tuple[int | None, dict[str, str], str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Astraa-Deployed-CORS-Smoke-Proof/1.0",
            "Origin": origin,
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(2048).decode("utf-8", errors="replace")
            headers = {key.lower(): value for key, value in response.headers.items()}
            return response.status, headers, body
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", errors="replace")
        headers = {key.lower(): value for key, value in exc.headers.items()}
        return exc.code, headers, body
    except Exception as exc:
        return None, {}, repr(exc)


def validate_https_url(label: str, value: str, failures: list[str]) -> bool:
    parsed = urlparse(value)

    if parsed.scheme != "https":
        failures.append(f"{label} must use HTTPS.")
        fail_line(f"{label} must use HTTPS.")
        return False

    if not parsed.netloc:
        failures.append(f"{label} is missing host.")
        fail_line(f"{label} is missing host.")
        return False

    if "*" in value:
        failures.append(f"{label} must not contain wildcard.")
        fail_line(f"{label} must not contain wildcard.")
        return False

    pass_line(f"{label} is a specific HTTPS URL.")
    return True


def main() -> int:
    failures: list[str] = []

    section("ASTRAA DEPLOYED CORS SMOKE PROOF")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    base_url = os.environ.get("ASTRAA_DEPLOYED_BASE_URL", "").strip()
    test_origin = os.environ.get("ASTRAA_CORS_TEST_ORIGIN", "").strip()
    test_path = os.environ.get("ASTRAA_CORS_TEST_PATH", "/health").strip() or "/health"

    section("CONFIGURATION")
    if not base_url:
        warn_line("ASTRAA_DEPLOYED_BASE_URL is not set.")
        warn_line("No deployed CORS smoke check was performed.")
        print("Result: SKIPPED")
        return 0

    if not test_origin:
        warn_line("ASTRAA_CORS_TEST_ORIGIN is not set.")
        warn_line("No deployed CORS smoke check was performed.")
        print("Result: SKIPPED")
        return 0

    print("ASTRAA_DEPLOYED_BASE_URL:", base_url)
    print("ASTRAA_CORS_TEST_ORIGIN:", test_origin)
    print("ASTRAA_CORS_TEST_PATH:", test_path)

    section("HTTPS URL CHECKS")
    base_ok = validate_https_url("ASTRAA_DEPLOYED_BASE_URL", base_url, failures)
    origin_ok = validate_https_url("ASTRAA_CORS_TEST_ORIGIN", test_origin, failures)

    section("CORS RESPONSE CHECK")
    target_url = base_url.rstrip("/") + "/" + test_path.lstrip("/")
    print("Target URL:", target_url)

    if base_ok and origin_ok:
        status, headers, body = request_with_origin(target_url, test_origin)

        if status is None:
            failures.append(f"CORS request failed: {body}")
            fail_line(f"CORS request failed: {body}")
        else:
            pass_line(f"Endpoint responded with HTTP {status}.")

            allow_origin = headers.get("access-control-allow-origin", "")
            vary = headers.get("vary", "")

            print("Access-Control-Allow-Origin:", allow_origin or "<not set>")
            print("Vary:", vary or "<not set>")
            print("Response preview:", body[:300].replace("\n", " "))

            if allow_origin == "*":
                failures.append("CORS returned wildcard Access-Control-Allow-Origin.")
                fail_line("CORS returned wildcard Access-Control-Allow-Origin.")
            elif allow_origin == test_origin:
                pass_line("CORS allows the provided approved test origin exactly.")
            elif not allow_origin:
                warn_line("No Access-Control-Allow-Origin header returned for this path.")
                warn_line("This may be acceptable for non-CORS health endpoints, but API CORS should be checked before paid launch.")
            else:
                failures.append(f"CORS returned unexpected Access-Control-Allow-Origin: {allow_origin}")
                fail_line(f"CORS returned unexpected Access-Control-Allow-Origin: {allow_origin}")
    else:
        warn_line("Skipped CORS request because URL validation failed.")

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
        print("DEPLOYED CORS SMOKE PROOF: FAIL")
        print("Failures:")
        for failure in failures:
            print("-", failure)
        return 1

    print("DEPLOYED CORS SMOKE PROOF: PASS")
    print("Deployed CORS behavior passed guarded smoke proof or returned no unsafe wildcard.")
    print("Next blocker after deployed Host/CORS smoke proofs: deployed Moneris regression.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
