#!/usr/bin/env python3
"""
Astraa Lead Channel Report

Reads inbound consent-based lead records and prints:
- lead counts
- status breakdown
- top product interest
- sales-channel signal
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
LEADS_FILE = DATA_DIR / "astraa_leads.jsonl"
SALES_SIGNAL_FILE = DATA_DIR / "astraa_sales_signal.json"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []

    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def main() -> int:
    leads = read_jsonl(LEADS_FILE)

    print("=" * 80)
    print("ASTRAA LEAD CHANNEL REPORT")
    print("=" * 80)

    print("Total leads:", len(leads))

    status_counts = Counter(lead.get("status", "Unknown") for lead in leads)
    interest_counts = Counter((lead.get("tool_interest") or "Unknown").lower() for lead in leads)
    source_counts = Counter(lead.get("source_page") or "Unknown" for lead in leads)

    print("\nStatus:")
    for key, value in status_counts.most_common():
        print(f"- {key}: {value}")

    print("\nTool interest:")
    for key, value in interest_counts.most_common():
        print(f"- {key}: {value}")

    print("\nLead source:")
    for key, value in source_counts.most_common():
        print(f"- {key}: {value}")

    if SALES_SIGNAL_FILE.exists():
        try:
            signal = json.loads(SALES_SIGNAL_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            signal = {}

        print("\nSales signal:")
        print("- sales_channel_signal:", signal.get("sales_channel_signal", "unknown"))
        print("- recommended_next_product_focus:", signal.get("recommended_next_product_focus", "unknown"))
    else:
        print("\nSales signal: not generated yet")

    print("\nReminder:")
    print("- Use this as a sales decision signal only.")
    print("- Do not auto-launch paid modules without operator approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
