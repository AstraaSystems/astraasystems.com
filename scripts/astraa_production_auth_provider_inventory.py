#!/usr/bin/env python3
"""
Astraa Production Auth Provider Inventory

READ-ONLY SCRIPT.

Purpose:
- Inventory current auth/session/provider readiness before production auth implementation.
- Locate where a future production auth provider/session resolver should plug in.
- Map dev-session usage, /api/auth/me, /api/auth/dev-login, bearer token resolution,
  account authority, request guards, and account/tenant identity references.

Does NOT:
- modify api.py
- change auth behavior
- create users
- create sessions
- connect to an auth provider
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
import json
import re
from collections import Counter
from datetime import datetime, timezone


ROOT = Path(".")
API_PATH = ROOT / "api.py"

PATTERNS = [
    "/api/auth/dev-login",
    "/api/auth/me",
    "dev-login",
    "auth/me",
    "dev_session",
    "dev_session_bearer_token",
    "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE",
    "ASTRAA_PUBLIC_LAUNCH_MODE",
    "ASTRAA_REQUEST_GUARD_ENABLED",
    "Authorization",
    "Bearer",
    "token",
    "session",
    "identity",
    "identity_source",
    "account_email",
    "account_id",
    "tenant_id",
    "selected_plan",
    "payment_status",
    "subscription_status",
    "account authority",
    "authorized account",
    "request guard",
    "astraa_resolve_session_identity",
    "astraa_get_bearer_token",
    "astraa_require_account_authority",
    "astraa_resolve_authorized_account",
    "jwt",
    "oauth",
    "oidc",
    "cookie",
    "login",
    "logout",
]

ROUTE_RE = re.compile(r'^\s*@app\.(route|get|post|put|delete|patch)\((.*)\)\s*$')
DEF_RE = re.compile(r'^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')
ENV_RE = re.compile(r'os\.getenv\(["\']([^"\']+)["\']')


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


def classify_function(function_name):
    lower = function_name.lower()

    if "auth" in lower or "login" in lower or "logout" in lower:
        return "auth_route_or_helper"
    if "session" in lower or "token" in lower or "bearer" in lower:
        return "session_token_helper"
    if "identity" in lower:
        return "identity_resolver"
    if "account" in lower or "tenant" in lower:
        return "account_tenant_authority"
    if "guard" in lower:
        return "security_guard"
    if "payment" in lower:
        return "payment_authority_related"

    return "other"


def main():
    section("ASTRAA PRODUCTION AUTH PROVIDER INVENTORY")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("File scanned:", API_PATH)

    if not API_PATH.exists():
        raise SystemExit("❌ api.py not found")

    lines = API_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()

    matches = []
    functions = []
    routes = []
    pending_routes = []
    env_refs = []

    for idx, line in enumerate(lines, 1):
        matched = [p for p in PATTERNS if p.lower() in line.lower()]
        if matched:
            matches.append({
                "line": idx,
                "matched": matched,
                "text": line.rstrip(),
                "context": context(lines, idx, 1),
            })

        for env_match in ENV_RE.findall(line):
            if any(keyword in env_match for keyword in ["AUTH", "LOGIN", "SESSION", "JWT", "OAUTH", "OIDC", "ASTRAA_PUBLIC", "REQUEST_GUARD"]):
                env_refs.append({
                    "line": idx,
                    "env": env_match,
                    "text": line.rstrip(),
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
            category = classify_function(function_name)

            if category != "other":
                functions.append({
                    "line": idx,
                    "function": function_name,
                    "category": category,
                    "context": context(lines, idx, 1),
                })

            if pending_routes:
                for route in pending_routes:
                    raw_l = route["raw"].lower()
                    if any(term in raw_l for term in ["auth", "payment", "account", "estimator", "core"]):
                        routes.append({
                            **route,
                            "function": function_name,
                            "function_category": category,
                        })
                pending_routes = []

    section("SUMMARY")
    print("Pattern matches:", len(matches))
    print("Relevant routes:", len(routes))
    print("Auth/session/account functions:", len(functions))
    print("Relevant env refs:", len(env_refs))

    section("ROUTES RELATED TO AUTH / ACCOUNT / PAYMENT / ESTIMATOR / CORE")
    if not routes:
        print("None")
    for route in routes:
        print(json.dumps(route, indent=2, sort_keys=True))

    section("AUTH / SESSION / IDENTITY / ACCOUNT FUNCTIONS")
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

    section("ENVIRONMENT REFERENCES")
    if not env_refs:
        print("None")
    for item in env_refs:
        print(json.dumps(item, indent=2, sort_keys=True))

    section("DETAILED MATCHES")
    if not matches:
        print("None")
    for item in matches:
        print(json.dumps(item, indent=2, sort_keys=True))

    section("PRODUCTION AUTH PROVIDER PLUG-IN NOTES")
    print("- Future provider resolver should plug into the same identity contract used by /api/auth/me.")
    print("- Dev-login should remain blocked in public launch mode by default.")
    print("- Existing backend account authority guard should remain the source of account truth.")
    print("- Estimator and payment routes should continue ignoring browser-submitted account_email for authorization.")
    print("- Core OS customer-facing routes should require tenant/account identity before public use.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not change auth behavior.")
    print("This script did not create users or sessions.")
    print("This script did not connect to an auth provider.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
