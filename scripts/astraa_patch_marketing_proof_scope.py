#!/usr/bin/env python3
"""
Astraa Patch: Marketing Proof Scope

PATCH SCRIPT.

Purpose:
- Keep marketing/public website proof separate from fully automated paid SaaS readiness proof.
- Remove launch_tracks_master_plan from marketing enablement proof because it includes paid SaaS blockers
  that are intentionally still NO-GO.
- Replace it with paid SaaS blocker/implementation documentation checks.
- Keep broad paid SaaS automation blocked until production auth, managed DB, secrets, host/TLS,
  and deployed Moneris regression pass.

Does NOT:
- modify api.py
- open customer access
- change backend/auth/payment behavior
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re


ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"marketing_proof_scope_{STAMP}"

TARGET = Path("scripts/astraa_marketing_enablement_proof.py")

OLD_PATTERNS = [
    r'\s*\("Launch tracks master plan",\s*\[sys\.executable,\s*"scripts/astraa_launch_tracks_master_plan.py"\]\),',
    r'\s*\("Launch tracks master plan",\s*\[sys\.executable,\s*\'scripts/astraa_launch_tracks_master_plan.py\'\]\),',
]

NEW_BLOCK = '''
    ("Paid SaaS blocker execution plan", [sys.executable, "scripts/astraa_paid_saas_blocker_execution_plan.py"]),
    ("Paid SaaS implementation lane", [sys.executable, "scripts/astraa_paid_saas_implementation_lane.py"]),
    ("Production auth provider selection decision", [sys.executable, "scripts/astraa_production_auth_provider_selection_decision.py"]),'''


def main():
    print("=" * 100)
    print("ASTRAA MARKETING PROOF SCOPE PATCH")
    print("=" * 100)
    print("Mode: PATCH SCRIPT")
    print("Target:", TARGET)
    print("Backup directory:", BACKUP_DIR)

    if not TARGET.exists():
        raise SystemExit(f"Missing target: {TARGET}")

    original = TARGET.read_text(encoding="utf-8", errors="ignore")
    text = original

    replaced = False
    for pattern in OLD_PATTERNS:
        new_text, count = re.subn(pattern, NEW_BLOCK, text)
        if count:
            text = new_text
            replaced = True
            print(f"Replaced launch tracks master plan reference using pattern: {pattern}")

    if not replaced:
        print("No launch tracks master plan command found. Checking whether scope may already be patched.")
        if "astraa_paid_saas_blocker_execution_plan.py" in text and "astraa_paid_saas_implementation_lane.py" in text:
            print("Marketing proof scope already appears patched.")
            return
        raise SystemExit("Could not patch marketing proof scope automatically.")

    backup_path = BACKUP_DIR / TARGET
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(original, encoding="utf-8")

    TARGET.write_text(text, encoding="utf-8")

    print("")
    print("PATCHED:", TARGET)
    print("")
    print("Safety confirmation:")
    print("- This patch did not modify api.py.")
    print("- This patch did not open customer access.")
    print("- This patch did not change backend/auth/payment behavior.")
    print("- This patch did not deploy Astraa.")
    print("- Paid SaaS readiness remains blocked by production auth/DB/secrets/TLS/Moneris regression.")


if __name__ == "__main__":
    main()
