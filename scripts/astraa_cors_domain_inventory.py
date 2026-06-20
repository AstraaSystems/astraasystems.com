#!/usr/bin/env python3
"""
Astraa CORS Domain Inventory

READ-ONLY SCRIPT.

Purpose:
- Inventory current CORS/domain behavior before patching.
- Locate flask_cors usage, CORS(app, ...), Access-Control-Allow-Origin headers,
  after_request hooks, Origin/header handling, localhost/domain references.

Does NOT:
- modify api.py
- change CORS behavior
- change deployment behavior
"""

from __future__ import annotations

from pathlib import Path
import json
import re
from collections import Counter


API_PATH = Path("api.py")

PATTERNS = [
    "flask_cors",
    "CORS(",
    "Access-Control-Allow-Origin",
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Methods",
    "after_request",
    "Origin",
    "origin",
    "localhost",
    "127.0.0.1",
    "astraasystems.com",
    "allowed_origins",
    "ALLOW",
    "CORS",
]

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
    section("ASTRAA CORS DOMAIN INVENTORY")
    print("Mode: READ ONLY")
    print("File scanned:", API_PATH)

    if not API_PATH.exists():
        raise SystemExit("❌ api.py not found")

    lines = API_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()

    matches = []
    functions = []

    for idx, line in enumerate(lines, 1):
        matched = [p for p in PATTERNS if p.lower() in line.lower()]
        if matched:
            matches.append({
                "line": idx,
                "matched": matched,
                "text": line.rstrip(),
                "context": context(lines, idx, 1),
            })

        def_match = DEF_RE.match(line)
        if def_match:
            function_name = def_match.group(1)
            if (
                "cors" in function_name.lower()
                or "origin" in function_name.lower()
                or "request" in function_name.lower()
                or "header" in function_name.lower()
            ):
                functions.append({
                    "line": idx,
                    "function": function_name,
                    "context": context(lines, idx, 1),
                })

    section("SUMMARY")
    print("Pattern matches:", len(matches))
    print("CORS/header-related functions:", len(functions))

    section("MATCHES BY PATTERN")
    counts = Counter()
    for item in matches:
        for pattern in item["matched"]:
            counts[pattern] += 1

    for pattern, count in counts.most_common():
        print(f"{pattern}: {count}")

    section("CORS / HEADER RELATED FUNCTIONS")
    if not functions:
        print("None")
    for item in functions:
        print(json.dumps(item, indent=2, sort_keys=True))

    section("DETAILED CORS / DOMAIN MATCHES")
    if not matches:
        print("None")
    for item in matches:
        print(json.dumps(item, indent=2, sort_keys=True))

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not change CORS behavior.")
    print("This script did not change deployment behavior.")


if __name__ == "__main__":
    main()
