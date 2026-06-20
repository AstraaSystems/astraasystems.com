#!/usr/bin/env python3
"""
Astraa Auth Hardening Inventory

READ-ONLY SCRIPT.

Purpose:
- Inventory current auth/session/dev-login implementation before production auth hardening.
- Locate:
  - /api/auth/dev-login
  - /api/auth/me
  - dev session token creation
  - bearer-token identity resolution
  - request guard/account authority functions
  - places where dev_session/dev_session_bearer_token still appear
  - auth/account_email/tenant_id references
  - routes that may need production auth enforcement later

Does NOT:
- modify files
- change auth behavior
- create users
- create sessions
- delete sessions
- migrate data
"""

from __future__ import annotations

from pathlib import Path
import json
import re
from collections import Counter


API_PATH = Path("api.py")

PATTERNS = [
    "dev-login",
    "auth/me",
    "astraa_dev_login",
    "astraa_auth_me",
    "astraa_resolve_session_identity",
    "astraa_issue_dev_session",
    "astraa_get_bearer_token",
    "dev_session",
    "dev_session_bearer_token",
    "Authorization",
    "Bearer",
    "account_email",
    "account_id",
    "tenant_id",
    "selected_plan",
    "identity_source",
    "ASTRAA_PUBLIC_LAUNCH_MODE",
    "ASTRAA_REQUEST_GUARD_ENABLED",
    "account authority",
    "request guard",
    "astraa_require_account_authority",
    "astraa_resolve_authorized_account",
    "payment verification blocked by account authority guard",
    "Browser sessionStorage",
    "sessionStorage",
]

ROUTE_RE = re.compile(r'^\s*@app\.(route|get|post|put|delete|patch)\((.*)\)\s*$')
DEF_RE = re.compile(r'^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def context(lines, line_no, radius=2):
    start = max(1, line_no - radius)
    end = min(len(lines), line_no + radius)
    return [
        {
            "line": idx,
            "text": lines[idx - 1].rstrip(),
        }
        for idx in range(start, end + 1)
    ]


def main():
    section("ASTRAA AUTH HARDENING INVENTORY")
    print("Mode: READ ONLY")
    print("File scanned:", API_PATH)

    if not API_PATH.exists():
        raise SystemExit("❌ api.py not found")

    lines = API_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()

    matches = []
    routes = []
    functions = []
    pending_routes = []

    for idx, line in enumerate(lines, 1):
        matched = [p for p in PATTERNS if p.lower() in line.lower()]
        if matched:
            matches.append({
                "line": idx,
                "matched": matched,
                "text": line.rstrip(),
                "context": context(lines, idx, 1),
            })

        route_match = ROUTE_RE.match(line)
        if route_match:
            pending_routes.append({
                "line": idx,
                "decorator": route_match.group(1),
                "raw": line.strip(),
            })
            continue

        def_match = DEF_RE.match(line)
        if def_match:
            function_name = def_match.group(1)

            if (
                "auth" in function_name.lower()
                or "session" in function_name.lower()
                or "identity" in function_name.lower()
                or "guard" in function_name.lower()
                or "account" in function_name.lower()
                or "bearer" in function_name.lower()
            ):
                functions.append({
                    "line": idx,
                    "function": function_name,
                    "context": context(lines, idx, 1),
                })

            if pending_routes:
                for route in pending_routes:
                    route_raw_l = route["raw"].lower()
                    if (
                        "auth" in route_raw_l
                        or "payment" in route_raw_l
                        or "account" in route_raw_l
                        or "estimator" in route_raw_l
                        or "core" in route_raw_l
                    ):
                        route_record = dict(route)
                        route_record["function"] = function_name
                        routes.append(route_record)

                pending_routes = []

    section("SUMMARY")
    print("Pattern matches:", len(matches))
    print("Relevant routes:", len(routes))
    print("Relevant functions:", len(functions))

    section("AUTH / ACCOUNT / PROTECTED ROUTES")
    if not routes:
        print("None")
    for route in routes:
        print(json.dumps(route, indent=2, sort_keys=True))

    section("AUTH / SESSION / ACCOUNT FUNCTIONS")
    if not functions:
        print("None")
    for item in functions:
        print(json.dumps(item, indent=2, sort_keys=True))

    section("MATCHES BY PATTERN")
    counts = Counter()
    for item in matches:
        for pattern in item["matched"]:
            counts[pattern] += 1

    for pattern, count in counts.most_common():
        print(f"{pattern}: {count}")

    section("DETAILED MATCHES")
    if not matches:
        print("None")
    for item in matches:
        print(json.dumps(item, indent=2, sort_keys=True))

    section("AUTH HARDENING NOTES")
    print("This inventory is informational only.")
    print("Potential future hardening areas to review manually:")
    print("- Replace /api/auth/dev-login with production auth provider/session flow.")
    print("- Keep /api/auth/me but resolve identity from production session/JWT.")
    print("- Keep account authority guard for payment and estimator routes.")
    print("- Ensure browser-submitted account_email never overrides authenticated identity.")
    print("- Decide whether dev-login route should be disabled in public launch mode.")
    print("- Confirm CORS/domain restrictions before public launch.")
    print("- Confirm session/token storage moves away from local dev-session JSON for production.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not create users.")
    print("This script did not create sessions.")
    print("This script did not delete sessions.")
    print("This script did not change auth behavior.")


if __name__ == "__main__":
    main()
