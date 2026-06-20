#!/usr/bin/env python3
"""
Astraa Patch: Visible Finance + Operations Pricing Cards

PATCH SCRIPT.

Purpose:
- Make Finance and Operations pricing visible directly in the top pricing cards.
- Match the Estimator pricing card style so customers do not need to scroll down.
- Patch pricing.html and frontend/pricing.html only.

Does NOT:
- modify api.py
- change Moneris/payment enforcement
- change backend pricing logic
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime


ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"visible_finance_operations_pricing_cards_{STAMP}"

TARGETS = [
    Path("pricing.html"),
    Path("frontend/pricing.html"),
]

REPLACEMENTS = [
    (
        "Included or assigned for light finance visibility based on customer type and package.",
        "$29.99 CAD/month. Single user. For small/startup businesses that need clear financial tracking."
    ),
    (
        "Fuller finance visibility with Expense connection and broader Workspace support.",
        "$79.99 CAD/month. Includes up to 3 users. For growing businesses that need stronger financial control."
    ),
    (
        "Quoted for custom finance workflows, organization size, non-profit needs, or setup requirements.",
        "Custom quote for franchises, contractors, multi-location teams, non-profit needs, or special reporting workflows."
    ),
    (
        "Limited operations visibility for simple action tracking and follow-up.",
        "$59.99 CAD/month. Single user. For small teams that need basic scheduling and job coordination."
    ),
    (
        "Broader operations support for owners, priorities, statuses, blockers, and summaries.",
        "$149.99 CAD/month. Includes up to 5 users. For crews, subcontractors, field updates, and operational visibility."
    ),
    (
        "Quoted for larger teams, contractor access, franchise workflows, or custom setup needs.",
        "Operations Plus starts at $299.99 CAD/month for up to 10 users. Custom quotes are available for larger teams, contractors, franchises, or special setup needs."
    ),
]


def patch_file(path: Path) -> bool:
    if not path.exists():
        print(f"SKIP missing: {path}")
        return False

    original = path.read_text(encoding="utf-8", errors="ignore")
    text = original

    for old, new in REPLACEMENTS:
        text = text.replace(old, new)

    if text == original:
        print(f"UNCHANGED: {path}")
        return False

    backup_path = BACKUP_DIR / path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(original, encoding="utf-8")

    path.write_text(text, encoding="utf-8")
    print(f"PATCHED: {path}")
    return True


def main():
    print("=" * 100)
    print("ASTRAA VISIBLE FINANCE + OPERATIONS PRICING CARDS PATCH")
    print("=" * 100)
    print("Mode: PATCH PUBLIC PRICING HTML ONLY")
    print("Backup directory:", BACKUP_DIR)

    changed = 0

    for path in TARGETS:
        if patch_file(path):
            changed += 1

    print("")
    print("Changed files:", changed)
    print("")
    print("Safety confirmation:")
    print("- This script did not modify api.py.")
    print("- This script did not change Moneris/payment enforcement.")
    print("- This script did not change backend pricing logic.")
    print("- This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
