#!/usr/bin/env python3
"""
Astraa Pricing Card Layout QA

READ-ONLY SCRIPT.

Purpose:
- Verify Finance and Operations visible pricing cards contain prices directly.
- Check pricing card text is not overly long for browser layout review.
- Confirm root and frontend pricing pages match expected launch pricing.

Does NOT:
- modify HTML
- deploy Astraa
- change backend/auth/payment behavior
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import re


TARGETS = [
    Path("pricing.html"),
    Path("frontend/pricing.html"),
]

REQUIRED_VISIBLE_TEXT = [
    "$29.99 CAD/month. Single user",
    "$79.99 CAD/month. Includes up to 3 users",
    "$59.99 CAD/month. Single user",
    "$149.99 CAD/month. Includes up to 5 users",
    "Operations Plus starts at $299.99 CAD/month",
]

SECTION_LABELS = [
    "Astraa Estimator pricing",
    "Astraa Finance pricing",
    "Astraa Operations pricing",
]

MAX_CARD_TEXT_LENGTH = 230


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def extract_card_texts(html: str):
    # Lightweight check: extracts common card body snippets around choice/pricing cards.
    snippets = []

    patterns = [
        r'<div class="mini">.*?</div>',
        r'<div class="choice-card".*?</div>\s*</div>',
        r'<article class="astraa-pricing-card.*?</article>',
    ]

    for pattern in patterns:
        for match in re.findall(pattern, html, flags=re.IGNORECASE | re.DOTALL):
            clean = re.sub(r"<.*?>", " ", match)
            clean = re.sub(r"\s+", " ", clean).strip()
            snippets.append(clean)

    return snippets


def check_file(path: Path):
    section(f"CHECKING {path}")

    if not path.exists():
        print(f"FAIL: Missing file {path}")
        return False

    html = path.read_text(encoding="utf-8", errors="ignore")
    ok = True

    print("File size:", len(html), "characters")

    section("Required section labels")
    for label in SECTION_LABELS:
        if label in html:
            print(f"PASS: Found section label: {label}")
        else:
            print(f"FAIL: Missing section label: {label}")
            ok = False

    section("Required visible pricing text")
    for text in REQUIRED_VISIBLE_TEXT:
        if text in html:
            print(f"PASS: Found visible pricing text: {text}")
        else:
            print(f"FAIL: Missing visible pricing text: {text}")
            ok = False

    section("Pricing card text length review")
    snippets = extract_card_texts(html)

    if not snippets:
        print("WARN: No pricing/card snippets extracted by static checker.")
    else:
        long_items = []
        for snippet in snippets:
            if any(price in snippet for price in ["$29.99", "$79.99", "$59.99", "$149.99", "$299.99"]):
                print(f"Card snippet ({len(snippet)} chars): {snippet}")
                if len(snippet) > MAX_CARD_TEXT_LENGTH:
                    long_items.append(snippet)

        if long_items:
            print("")
            print("WARN: Some visible pricing card text may be long for small screens:")
            for item in long_items:
                print("-", item)
            print("Manual browser check required for wrapping/crowding.")
        else:
            print("PASS: Visible pricing card snippets are within static length threshold.")

    return ok


def main():
    section("ASTRAA PRICING CARD LAYOUT QA")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    all_ok = True

    for path in TARGETS:
        if not check_file(path):
            all_ok = False

    section("QA SUMMARY")
    if all_ok:
        print("✅ STATIC PRICING CARD QA PASSED")
        print("Next: open pricing.html in browser and confirm visual spacing.")
    else:
        print("❌ STATIC PRICING CARD QA FAILED")
        print("Fix missing visible pricing text before browser QA.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify HTML.")
    print("This script did not deploy Astraa.")
    print("This script did not change backend/auth/payment behavior.")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
