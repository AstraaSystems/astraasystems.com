#!/usr/bin/env python3
"""
Astraa ↔ Arka Bridge Report

Shows internal communication status between Astraa event logging and Arka recommendations.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from astraa_arka_bridge import get_bridge_summary


def main() -> int:
    summary = get_bridge_summary()

    print("=" * 80)
    print("ASTRAA ↔ ARKA BRIDGE REPORT")
    print("=" * 80)

    print("Events sent to Arka:", summary["events_to_arka"])
    print("Recommendations from Arka:", summary["recommendations_from_arka"])

    print("\nLatest event:")
    print(summary["latest_event"])

    print("\nLatest recommendation:")
    print(summary["latest_recommendation"])

    print("\nBoundary:")
    print("- Astraa sends structured events.")
    print("- Arka returns recommendations.")
    print("- Operator approval remains required for production actions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
