#!/usr/bin/env python3
"""
Astraa Patch: Public Access Wording Cleanup

PATCH SCRIPT.

Purpose:
- Clean public/access pages before marketing launch.
- Replace outdated engines.html links with tools.html.
- Remove internal Arkastra naming from login/register access pages.

Targets:
- login.html
- frontend/login.html
- register.html
- frontend/register.html

Does NOT:
- modify api.py
- change auth behavior
- change payment behavior
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime


ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"public_access_wording_cleanup_{STAMP}"

TARGETS = [
    Path("login.html"),
    Path("frontend/login.html"),
    Path("register.html"),
    Path("frontend/register.html"),
]

REPLACEMENTS = [
    ('href="engines.html"', 'href="tools.html"'),
    ("href='engines.html'", "href='tools.html'"),
    ("Arkastra Commerce Tool", "Commerce Tool"),
    ("Arkastra Commerce", "Commerce"),
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
    print("ASTRAA PUBLIC ACCESS WORDING CLEANUP")
    print("=" * 100)
    print("Mode: PATCH PUBLIC ACCESS HTML ONLY")
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
    print("- This script did not change auth behavior.")
    print("- This script did not change payment behavior.")
    print("- This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
