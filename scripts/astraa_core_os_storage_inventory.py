#!/usr/bin/env python3
"""
Astraa Core OS Storage Inventory

READ-ONLY SCRIPT.
Scans api.py for Core OS storage, route, and helper references.

Purpose:
- Identify Core OS file-backed persistence before abstraction work.
- Map routes and functions related to:
  - Core session
  - Core entity
  - Core activity
  - Core vault records
  - Core events
  - Core search
- Does not modify files.
"""

from __future__ import annotations

from pathlib import Path
import json
import re


API_PATH = Path("api.py")

PATTERNS = [
    "ASTRAA_CORE_STORE_PATH",
    "astraa_core_default_store",
    "astraa_core_load_store",
    "astraa_core_save_store",
    "ASTRAA_CORE_STORE",
    "ASTRAA_CORE_ENTITIES",
    "ASTRAA_CORE_ACTIVITY",
    "ASTRAA_CORE_EVENTS",
    "ASTRAA_CORE_VAULT",
    "astraa_core_upsert_entity",
    "astraa_core_write_activity",
    "astraa_core_upsert_vault_record",
    "astraa_core_search",
    "astraa_core_session",
    "astraa_core_entity",
    "astraa_core_activity",
    "astraa_core_vault_record",
    "astraa_core_event",
    "astraa_core_now",
    "astraa_core_id",
    "/api/astraa/core/session",
    "/api/astraa/core/entity",
    "/api/astraa/core/activity",
    "/api/astraa/core/vault-record",
    "/api/astraa/core/event",
    "/api/astraa/core/search",
    "astraa_core_os_store.json",
]

ROUTE_RE = re.compile(r'^\s*@app\.(route|get|post|put|delete|patch)\((.*)\)\s*$')
DEF_RE = re.compile(r'^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')


def context(lines, line_no, radius=2):
    start = max(1, line_no - radius)
    end = min(len(lines), line_no + radius)
    return [
        {
            "line": idx,
            "text": lines[idx - 1].rstrip()
        }
        for idx in range(start, end + 1)
    ]


def main():
    if not API_PATH.exists():
        raise SystemExit("api.py not found")

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

            if function_name.startswith("astraa_core"):
                functions.append({
                    "line": idx,
                    "function": function_name,
                    "context": context(lines, idx, 1),
                })

            if pending_routes:
                for route in pending_routes:
                    if "/api/astraa/core/" in route["raw"]:
                        route_record = dict(route)
                        route_record["function"] = function_name
                        routes.append(route_record)
                pending_routes = []

    print("=" * 100)
    print("ASTRAA CORE OS STORAGE INVENTORY")
    print("=" * 100)
    print("Mode: READ ONLY")
    print("File scanned:", API_PATH)
    print("Pattern matches:", len(matches))
    print("Core routes:", len(routes))
    print("Core functions:", len(functions))

    print("\nCORE ROUTES:")
    if not routes:
        print("None")
    for route in routes:
        print(json.dumps(route, indent=2, sort_keys=True))

    print("\nCORE FUNCTIONS:")
    if not functions:
        print("None")
    for item in functions:
        print(json.dumps(item, indent=2, sort_keys=True))

    print("\nCORE STORAGE MATCHES:")
    if not matches:
        print("None")
    for item in matches:
        print(json.dumps(item, indent=2, sort_keys=True))

    print("\nSummary by pattern:")
    counts = {}
    for item in matches:
        for p in item["matched"]:
            counts[p] = counts.get(p, 0) + 1

    for pattern, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"{pattern}: {count}")

    print("\nREAD-ONLY CONFIRMATION:")
    print("This script did not modify any file.")


if __name__ == "__main__":
    main()
