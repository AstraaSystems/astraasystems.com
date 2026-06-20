#!/usr/bin/env python3
"""
Astraa CORS Acceptance Tests

LOCAL RUNTIME TEST SCRIPT.

Purpose:
- Verify public-launch-mode CORS behavior after domain lock patch.
- Tests:
  - allowed production origin receives matching Access-Control-Allow-Origin
  - unknown origin does not receive wildcard or matching CORS allow header
  - localhost origin is allowed only when ASTRAA_ALLOW_LOCALHOST_CORS=true
  - OPTIONS preflight receives allowed-origin response

Does NOT:
- modify source files
- modify CORS implementation
- migrate data
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone


BASE_URL = "http://localhost:5000"

ALLOWED_ORIGIN = os.getenv("ASTRAA_CORS_TEST_ALLOWED_ORIGIN", "https://astraasystems.com")
UNKNOWN_ORIGIN = os.getenv("ASTRAA_CORS_TEST_UNKNOWN_ORIGIN", "https://evil.example.com")
LOCALHOST_ORIGIN = os.getenv("ASTRAA_CORS_TEST_LOCALHOST_ORIGIN", "http://localhost:5000")


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def request_with_origin(path, origin, method="GET", extra_headers=None):
    headers = {"Origin": origin}

    if extra_headers:
        headers.update(extra_headers)

    req = urllib.request.Request(
        BASE_URL + path,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, dict(resp.headers), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers), body
    except Exception as exc:
        return 0, {}, str(exc)


def check(condition, label, details=None):
    if condition:
        print(f"PASS: {label}")
        return True

    print(f"FAIL: {label}")

    if details is not None:
        print(json.dumps(details, indent=2, sort_keys=True))

    return False


def header(headers, name):
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def main():
    section("ASTRAA CORS ACCEPTANCE TESTS")
    print("Mode: LOCAL RUNTIME TEST")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Base URL:", BASE_URL)
    print("Allowed origin:", ALLOWED_ORIGIN)
    print("Unknown origin:", UNKNOWN_ORIGIN)
    print("Localhost origin:", LOCALHOST_ORIGIN)
    print("ASTRAA_ALLOW_LOCALHOST_CORS:", os.getenv("ASTRAA_ALLOW_LOCALHOST_CORS"))

    results = []

    section("1. ALLOWED PRODUCTION ORIGIN")
    status, headers, body = request_with_origin("/health", ALLOWED_ORIGIN)
    acao = header(headers, "Access-Control-Allow-Origin")

    results.append(check(
        status == 200 and acao == ALLOWED_ORIGIN,
        "Allowed production origin receives matching Access-Control-Allow-Origin",
        {
            "status": status,
            "access_control_allow_origin": acao,
        },
    ))

    section("2. UNKNOWN ORIGIN")
    status, headers, body = request_with_origin("/health", UNKNOWN_ORIGIN)
    acao = header(headers, "Access-Control-Allow-Origin")

    results.append(check(
        status == 200 and acao not in {"*", UNKNOWN_ORIGIN},
        "Unknown origin is not wildcard-allowed and not echoed",
        {
            "status": status,
            "access_control_allow_origin": acao,
        },
    ))

    section("3. LOCALHOST ORIGIN")
    status, headers, body = request_with_origin("/health", LOCALHOST_ORIGIN)
    acao = header(headers, "Access-Control-Allow-Origin")

    localhost_expected = os.getenv("ASTRAA_ALLOW_LOCALHOST_CORS", "false").strip().lower() == "true"

    if localhost_expected:
        condition = status == 200 and acao == LOCALHOST_ORIGIN
        label = "Localhost origin is allowed when ASTRAA_ALLOW_LOCALHOST_CORS=true"
    else:
        condition = status == 200 and acao not in {"*", LOCALHOST_ORIGIN}
        label = "Localhost origin is denied when ASTRAA_ALLOW_LOCALHOST_CORS is not true"

    results.append(check(
        condition,
        label,
        {
            "status": status,
            "access_control_allow_origin": acao,
        },
    ))

    section("4. ALLOWED ORIGIN PREFLIGHT")
    status, headers, body = request_with_origin(
        "/api/auth/me",
        ALLOWED_ORIGIN,
        method="OPTIONS",
        extra_headers={
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization, Content-Type",
        },
    )

    acao = header(headers, "Access-Control-Allow-Origin")

    results.append(check(
        status in {200, 204} and acao == ALLOWED_ORIGIN,
        "Allowed production origin preflight receives matching Access-Control-Allow-Origin",
        {
            "status": status,
            "access_control_allow_origin": acao,
            "body_preview": body[:300],
        },
    ))

    section("SUMMARY")
    passed = sum(1 for result in results if result)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ CORS ACCEPTANCE TESTS PASSED")
        raise SystemExit(0)

    print("❌ CORS ACCEPTANCE TESTS FAILED")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
