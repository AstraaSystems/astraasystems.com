#!/usr/bin/env python3
"""
Astraa Route and Function Inventory

READ-ONLY SCRIPT.
Scans api.py for Flask routes and function definitions.
Does not modify files.

Purpose:
- Identify duplicate route paths.
- Identify duplicate function names.
- Help avoid patching the wrong legacy block before storage abstraction work.
"""

from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import json
import re


API_PATH = Path("api.py")


ROUTE_RE = re.compile(r'^\s*@app\.(route|get|post|put|delete|patch)\((.*)\)\s*$')
DEF_RE = re.compile(r'^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')


def main():
    if not API_PATH.exists():
        raise SystemExit("api.py not found")

    lines = API_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()

    functions = []
    routes = []
    pending_routes = []

    for idx, line in enumerate(lines, 1):
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

            functions.append({
                "line": idx,
                "function": function_name,
            })

            if pending_routes:
                for route in pending_routes:
                    route_record = dict(route)
                    route_record["function"] = function_name
                    routes.append(route_record)
                pending_routes = []

    function_map = defaultdict(list)
    for item in functions:
        function_map[item["function"]].append(item["line"])

    route_map = defaultdict(list)
    for route in routes:
        route_map[route["raw"]].append({
            "line": route["line"],
            "function": route["function"],
        })

    duplicate_functions = {
        name: lines_
        for name, lines_ in function_map.items()
        if len(lines_) > 1
    }

    duplicate_routes = {
        route: items
        for route, items in route_map.items()
        if len(items) > 1
    }

    print("=" * 100)
    print("ASTRAA ROUTE AND FUNCTION INVENTORY")
    print("=" * 100)
    print("Mode: READ ONLY")
    print("File scanned:", API_PATH)
    print("Total functions:", len(functions))
    print("Total routes:", len(routes))
    print("Duplicate function names:", len(duplicate_functions))
    print("Duplicate route decorators:", len(duplicate_routes))

    print("\nROUTES:")
    for route in routes:
        print(json.dumps(route, indent=2, sort_keys=True))

    print("\nDUPLICATE FUNCTIONS:")
    if not duplicate_functions:
        print("None")
    else:
        for name, lines_ in sorted(duplicate_functions.items()):
            print(json.dumps({
                "function": name,
                "lines": lines_,
            }, indent=2, sort_keys=True))

    print("\nDUPLICATE ROUTE DECORATORS:")
    if not duplicate_routes:
        print("None")
    else:
        for route, items in sorted(duplicate_routes.items()):
            print(json.dumps({
                "route": route,
                "items": items,
            }, indent=2, sort_keys=True))

    print("\nREAD-ONLY CONFIRMATION:")
    print("This script did not modify any file.")


if __name__ == "__main__":
    main()
