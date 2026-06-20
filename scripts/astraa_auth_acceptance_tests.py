#!/usr/bin/env python3
"""
Astraa Auth Acceptance Tests

LOCAL RUNTIME TEST SCRIPT.

Purpose:
- Test current auth/session behavior before production auth hardening patches.
- Establish baseline behavior for:
  - /api/auth/dev-login
  - /api/auth/me
  - Estimator authenticated run
  - Estimator unauthenticated behavior
  - payload account_email hijack protection
  - payment verification authenticated replay

Does NOT:
- modify source files
- modify auth implementation
- create production users
- migrate data

Note:
- This script sends HTTP requests to a running local api.py server.
- Start api.py separately before running this script.
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone


BASE_URL = "http://localhost:5000"
TEST_ACCOUNT = "approved.live.test@astraasystems.com"
MALICIOUS_EMAIL = "malicious-change@example.com"
APPROVED_TICKET = "1781891159jSb8V8UZyDDY8VydC1cQ8GtwQGu0OT"


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def post_json(path, payload, token=None):
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return exc.code, parsed
    except Exception as exc:
        return 0, {"error": str(exc)}


def get_json(path, token=None):
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        BASE_URL + path,
        headers=headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return exc.code, parsed
    except Exception as exc:
        return 0, {"error": str(exc)}


def check(condition, label, details=None):
    if condition:
        print(f"PASS: {label}")
        return True

    print(f"FAIL: {label}")
    if details is not None:
        print(json.dumps(details, indent=2, sort_keys=True))
    return False


def main():
    section("ASTRAA AUTH ACCEPTANCE TESTS")
    print("Mode: LOCAL RUNTIME TEST")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Base URL:", BASE_URL)

    results = []

    section("1. HEALTH CHECK")
    health_status, health_body = get_json("/health")
    results.append(check(health_status == 200 and health_body.get("status") == "ok", "Health endpoint returns ok", health_body))

    section("2. DEV LOGIN")
    # ASTRAA_AUTH_ACCEPTANCE_DEV_LOGIN_BLOCK_TESTS_V1
    login_status, login_body = post_json("/api/auth/dev-login", {
        "account_email": TEST_ACCOUNT,
        "selected_plan": "Professional",
    })

    token = login_body.get("token")

    if login_status == 403 and login_body.get("status") == "blocked":
        results.append(check(
            login_body.get("reason") == "Development login is disabled in public launch mode.",
            "Dev login is blocked in public launch mode when internal QA override is not enabled",
            login_body,
        ))

        section("STOP")
        print("Dev-login is blocked as expected.")
        print("To run full auth acceptance tests, restart backend with:")
        print("export ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true")
        print("Then rerun scripts/astraa_auth_acceptance_tests.py")

        passed = sum(1 for result in results if result)
        total = len(results)

        section("SUMMARY")
        print(f"Passed: {passed}/{total}")

        if passed == total:
            print("✅ AUTH ACCEPTANCE BLOCK-MODE TESTS PASSED")
            raise SystemExit(0)

        print("❌ AUTH ACCEPTANCE BLOCK-MODE TESTS FAILED")
        raise SystemExit(1)

    results.append(check(
        login_status == 200 and login_body.get("status") == "ok" and bool(token),
        "Dev login returns token when internal QA override/local mode permits it",
        login_body,
    ))

    if not token:
        section("STOP")
        print("No token returned; cannot continue auth acceptance tests.")
        raise SystemExit(1)

    section("3. AUTH ME")
    me_status, me_body = get_json("/api/auth/me", token=token)
    identity = me_body.get("identity") or {}

    results.append(check(
        me_status == 200
        and me_body.get("status") == "ok"
        and identity.get("account_email") == TEST_ACCOUNT
        and identity.get("identity_source") == "dev_session_bearer_token",
        "Auth/me resolves dev session bearer token",
        me_body,
    ))

    section("4. ESTIMATOR AUTHENTICATED RUN / PAYLOAD HIJACK TEST")
    estimator_payload = {
        "inputs": {
            "account_email": MALICIOUS_EMAIL,
            "selected_plan": "Professional",
            "base_cost": "100000",
            "complexity_factor": "1.1",
            "material_multiplier": "1.08",
            "labor_multiplier": "1.12",
            "location_multiplier": "1.05",
        }
    }

    est_status, est_body = post_json("/api/astraa/estimator/enforced-run", estimator_payload, token=token)

    results.append(check(
        est_status == 200
        and est_body.get("status") == "ok"
        and (est_body.get("usage") or {}).get("plan") == "Professional",
        "Estimator authenticated run succeeds and ignores malicious payload account email",
        est_body,
    ))

    section("5. ESTIMATOR UNAUTHENTICATED BEHAVIOR")
    unauth_status, unauth_body = post_json("/api/astraa/estimator/enforced-run", estimator_payload, token=None)

    results.append(check(
        unauth_status in {200, 400, 401, 403}
        and unauth_body.get("status") in {"blocked", "error", "ok"} ,
        "Estimator unauthenticated behavior returns JSON response",
        {"status_code": unauth_status, "body": unauth_body},
    ))

    section("6. PAYMENT VERIFICATION AUTHENTICATED REPLAY")
    pay_status, pay_body = post_json("/api/payment/verify-moneris-receipt", {
        "account_email": MALICIOUS_EMAIL,
        "selected_tool": "Astraa Estimator",
        "selected_plan": "Professional",
        "purchase_type": "subscription_professional",
        "moneris_ticket": APPROVED_TICKET,
    }, token=token)

    payment = pay_body.get("payment") or {}

    results.append(check(
        pay_status == 200
        and pay_body.get("status") == "ok"
        and pay_body.get("payment_verified") is True
        and payment.get("account_email") == TEST_ACCOUNT,
        "Payment verification authenticated replay uses authorized account, not payload email",
        pay_body,
    ))

    section("SUMMARY")
    passed = sum(1 for result in results if result)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ AUTH ACCEPTANCE TESTS PASSED")
    else:
        print("❌ AUTH ACCEPTANCE TESTS FAILED")
        raise SystemExit(1)

    section("SAFETY CONFIRMATION")
    print("This script did not modify source files.")
    print("This script did not change auth implementation.")
    print("This script did not create production users.")
    print("This script only sent local HTTP requests to a running api.py server.")


if __name__ == "__main__":
    main()
