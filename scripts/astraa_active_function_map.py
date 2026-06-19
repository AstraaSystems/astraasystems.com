#!/usr/bin/env python3
"""
Astraa Active Function Map

READ-ONLY SCRIPT.
Scans api.py for duplicate function definitions and identifies which definition is active.

Python behavior:
- When the same function name is defined multiple times in a module,
  the later definition overrides the earlier name binding.

Purpose:
- Identify active helper implementations before storage abstraction work.
- Mark earlier duplicate definitions as shadowed/legacy candidates.
- Avoid patching inactive/legacy code blocks.

Does not modify files.
"""

from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import json
import re


API_PATH = Path("api.py")
DEF_RE = re.compile(r'^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')


FOCUS_PREFIXES = [
    "astraa_load_",
    "astraa_save_",
    "astraa_get_usage",
    "astraa_default_usage",
    "astraa_enforce_estimator_usage",
    "astraa_record_successful_estimator_usage",
    "astraa_apply_verified_payment",
    "astraa_payment",
    "astraa_validate",
]


def get_context(lines, line_number, radius=2):
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)
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

    function_lines = defaultdict(list)

    for idx, line in enumerate(lines, 1):
        match = DEF_RE.match(line)
        if match:
            function_lines[match.group(1)].append(idx)

    duplicates = {
        name: defs
        for name, defs in function_lines.items()
        if len(defs) > 1
    }

    focus_functions = {
        name: defs
        for name, defs in function_lines.items()
        if any(name.startswith(prefix) or name == prefix for prefix in FOCUS_PREFIXES)
    }

    active_duplicate_map = []

    for name, defs in sorted(duplicates.items()):
        active_line = max(defs)
        shadowed_lines = [line for line in defs if line != active_line]

        active_duplicate_map.append({
            "function": name,
            "active_line": active_line,
            "shadowed_lines": shadowed_lines,
            "all_definitions": defs,
            "active_context": get_context(lines, active_line),
        })

    print("=" * 100)
    print("ASTRAA ACTIVE FUNCTION MAP")
    print("=" * 100)
    print("Mode: READ ONLY")
    print("File scanned:", API_PATH)
    print("Total function names:", len(function_lines))
    print("Duplicate function names:", len(duplicates))
    print("Focused storage/payment/usage-related functions:", len(focus_functions))

    print("\nDUPLICATE FUNCTION ACTIVE MAP:")
    if not active_duplicate_map:
        print("None")
    else:
        for item in active_duplicate_map:
            print(json.dumps(item, indent=2, sort_keys=True))

    print("\nFOCUSED FUNCTIONS:")
    for name, defs in sorted(focus_functions.items()):
        print(json.dumps({
            "function": name,
            "definitions": defs,
            "active_line": max(defs),
            "shadowed_lines": [line for line in defs if line != max(defs)],
        }, indent=2, sort_keys=True))

    print("\nREAD-ONLY CONFIRMATION:")
    print("This script did not modify any file.")


if __name__ == "__main__":
    main()
