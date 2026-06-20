#!/usr/bin/env python3
"""
Astraa Public Website Risk Classifier

READ-ONLY SCRIPT.

Purpose:
- Run the public website inventory.
- Extract internal/public wording risk hits.
- Classify risk hits into review buckets for marketing launch QA.

Does NOT:
- modify website files
- deploy Astraa
- change backend behavior
- change auth/payment behavior
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

INTERNAL_OR_QA_FILES = [
    "internal-test.html",
    "workspace-internal.html",
    "workspace-test-login.html",
]

LEGAL_OR_PAYMENT_FILES = [
    "terms.html",
    "trial-terms.html",
    "payment.html",
    "payment-success.html",
]

PUBLIC_MARKETING_FILES = [
    "index.html",
    "tools.html",
    "pricing.html",
    "tool-finance.html",
    "tool-operations.html",
    "pricing-nonprofit.html",
    "pricing-contractor.html",
    "pricing-franchise.html",
    "contact.html",
    "about.html",
    "trial.html",
    "support.html",
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def classify_file(file_path: str) -> str:
    name = Path(file_path).name

    if name in INTERNAL_OR_QA_FILES:
        return "ACCEPTABLE_INTERNAL_PAGE"

    if name in LEGAL_OR_PAYMENT_FILES:
        return "ACCEPTABLE_LEGAL_OR_PAYMENT_CONTEXT"

    if name in PUBLIC_MARKETING_FILES:
        return "MUST_REVIEW_PUBLIC"

    if "login" in name or "register" in name:
        return "MUST_REVIEW_ACCESS_PAGE"

    return "MUST_REVIEW_UNKNOWN"


def run_inventory():
    proc = subprocess.run(
        [sys.executable, "scripts/astraa_public_website_file_inventory.py"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(proc.returncode)

    return proc.stdout


def extract_json_blocks(text: str):
    blocks = []
    current = []
    depth = 0
    in_block = False

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("{"):
            in_block = True
            current = [line]
            depth = stripped.count("{") - stripped.count("}")
            if depth == 0:
                blocks.append("\n".join(current))
                in_block = False
            continue

        if in_block:
            current.append(line)
            depth += stripped.count("{") - stripped.count("}")
            if depth == 0:
                blocks.append("\n".join(current))
                in_block = False

    parsed = []
    for block in blocks:
        try:
            obj = json.loads(block)
            if "file" in obj and "matched" in obj:
                parsed.append(obj)
        except Exception:
            pass

    return parsed


def main():
    section("ASTRAA PUBLIC WEBSITE RISK CLASSIFIER")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    inventory_output = run_inventory()
    risk_hits = extract_json_blocks(inventory_output)

    buckets = {}

    for hit in risk_hits:
        bucket = classify_file(hit.get("file", ""))
        buckets.setdefault(bucket, []).append(hit)

    section("SUMMARY")
    print("Total risk hits:", len(risk_hits))

    for bucket, items in sorted(buckets.items()):
        print(f"{bucket}: {len(items)}")

    section("MUST REVIEW ITEMS")
    for bucket in ["MUST_REVIEW_PUBLIC", "MUST_REVIEW_ACCESS_PAGE", "MUST_REVIEW_UNKNOWN"]:
        items = buckets.get(bucket, [])
        if not items:
            continue

        print("\n" + bucket)
        for item in items:
            print(json.dumps(item, indent=2, sort_keys=True))

    section("LOWER PRIORITY / CONTEXTUAL ITEMS")
    for bucket in ["ACCEPTABLE_INTERNAL_PAGE", "ACCEPTABLE_LEGAL_OR_PAYMENT_CONTEXT"]:
        items = buckets.get(bucket, [])
        print(f"{bucket}: {len(items)}")

    section("QA DECISION GUIDE")
    print("- MUST_REVIEW_PUBLIC should be cleaned before marketing launch if it exposes internal names or implementation details.")
    print("- MUST_REVIEW_ACCESS_PAGE should be reviewed because login/register/payment pages are customer-facing access paths.")
    print("- ACCEPTABLE_INTERNAL_PAGE can remain if those pages are not publicly linked or indexed.")
    print("- ACCEPTABLE_LEGAL_OR_PAYMENT_CONTEXT may be acceptable if wording is legally necessary and not marketing copy.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify website files.")
    print("This script did not deploy Astraa.")
    print("This script did not change backend behavior.")
    print("This script did not change auth/payment behavior.")


if __name__ == "__main__":
    main()
