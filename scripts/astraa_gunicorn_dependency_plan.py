#!/usr/bin/env python3
"""
Astraa Gunicorn Dependency Plan

READ-ONLY SCRIPT.

Purpose:
- Plan adding Gunicorn as a production/deployment dependency.
- Inspect whether requirements files exist.
- Print safe install and verification commands.
- Avoid modifying dependencies until explicitly reviewed.

Does NOT:
- install packages
- modify requirements.txt
- modify pyproject.toml
- modify api.py
- modify wsgi.py
- start Gunicorn
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

DEPENDENCY_FILES = [
    "requirements.txt",
    "requirements-prod.txt",
    "pyproject.toml",
    "Pipfile",
    "poetry.lock",
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def read_file_preview(path: Path, max_lines=80):
    if not path.exists():
        return []

    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()[:max_lines]
    except Exception as exc:
        return [f"Could not read file: {exc}"]


def file_mentions_gunicorn(path: Path):
    if not path.exists():
        return False

    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    return "gunicorn" in text


def main():
    section("ASTRAA GUNICORN DEPENDENCY PLAN")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Repository root:", ROOT)

    section("DEPENDENCY FILE INVENTORY")
    found_any = False
    gunicorn_found = False

    for file_name in DEPENDENCY_FILES:
        path = ROOT / file_name

        if path.exists():
            found_any = True
            mentions = file_mentions_gunicorn(path)
            gunicorn_found = gunicorn_found or mentions

            print(f"FOUND: {file_name}")
            print(f"Mentions gunicorn: {mentions}")

            preview = read_file_preview(path, max_lines=40)
            if preview:
                print("Preview:")
                for line in preview:
                    print("  " + line)
        else:
            print(f"MISSING: {file_name}")

        print("")

    section("CURRENT ASSESSMENT")
    if gunicorn_found:
        print("Gunicorn appears to already be listed in a dependency file.")
    elif found_any:
        print("Dependency file(s) exist, but Gunicorn was not found.")
    else:
        print("No common Python dependency file was found.")

    section("RECOMMENDED SAFE OPTIONS")
    print("Option A — Local venv test only, no repo dependency change yet:")
    print("  pip install gunicorn")
    print("  python3 scripts/astraa_gunicorn_local_smoke_test.py")
    print("")
    print("Option B — Add deployment dependency to requirements.txt after review:")
    print("  echo 'gunicorn' >> requirements.txt")
    print("  pip install -r requirements.txt")
    print("  python3 scripts/astraa_gunicorn_local_smoke_test.py")
    print("")
    print("Option C — Use separate production dependency file:")
    print("  echo 'gunicorn' >> requirements-prod.txt")
    print("  pip install -r requirements-prod.txt")
    print("  python3 scripts/astraa_gunicorn_local_smoke_test.py")

    section("RECOMMENDED ASTRAA PATH")
    print("1. If requirements.txt already drives deployment, add gunicorn there after review.")
    print("2. If you want to keep local dev lean, create requirements-prod.txt.")
    print("3. Do not install or commit dependency changes until this plan is reviewed.")
    print("4. After adding Gunicorn, rerun Gunicorn local smoke test.")
    print("5. Then run CORS hardening proof and post-auth-hardening proof.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not install packages.")
    print("This script did not modify requirements files.")
    print("This script did not modify api.py or wsgi.py.")
    print("This script did not start Gunicorn.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
