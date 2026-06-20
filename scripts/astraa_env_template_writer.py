#!/usr/bin/env python3
"""
Astraa Production Env Template Writer

SAFE BY DEFAULT.

Purpose:
- Write a placeholder-only production environment template into deployment_templates/.
- Refuse by default unless ASTRAA_ALLOW_TEMPLATE_FILE_WRITE=true.

Does NOT:
- write real secrets
- write to /etc
- modify system files
- deploy Astraa
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "deployment_templates"
ENV_FILE = TEMPLATE_DIR / "astraa-api.env.template"

ALLOW_WRITE = os.getenv("ASTRAA_ALLOW_TEMPLATE_FILE_WRITE", "false").strip().lower() == "true"

ENV_TEMPLATE = """
# Astraa API production-style environment template
# PLACEHOLDERS ONLY — do not commit real secrets.

ASTRAA_PUBLIC_LAUNCH_MODE=true
ASTRAA_REQUEST_GUARD_ENABLED=true
ASTRAA_STORAGE_BACKEND=json
ASTRAA_ALLOWED_ORIGINS=https://astraasystems.com,https://www.astraasystems.com
ASTRAA_ALLOW_LOCALHOST_CORS=false

# Must remain unset or false in production.
ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=false

MONERIS_ENV=prod
MONERIS_STORE_ID=REPLACE_WITH_SECURE_SECRET
MONERIS_API_TOKEN=REPLACE_WITH_SECURE_SECRET
MONERIS_CHECKOUT_ID=REPLACE_WITH_SECURE_SECRET
ASTRAA_TEST_AMOUNT=2.00
""".strip() + "\n"


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def is_safe_template_path(path: Path) -> bool:
    resolved = path.resolve()
    root = ROOT.resolve()

    if not str(resolved).startswith(str(root)):
        return False

    return "deployment_templates" in resolved.parts


def main():
    section("ASTRAA PRODUCTION ENV TEMPLATE WRITER")
    print("Mode:", "WRITE ENABLED" if ALLOW_WRITE else "READ ONLY / REFUSAL BY DEFAULT")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Template path:", ENV_FILE)

    section("TEMPLATE PREVIEW")
    print(ENV_TEMPLATE)

    section("WRITE BEHAVIOR")
    if not ALLOW_WRITE:
        print("Refusing to write because ASTRAA_ALLOW_TEMPLATE_FILE_WRITE is not true.")
        print("")
        print("To intentionally write local placeholder template only:")
        print("export ASTRAA_ALLOW_TEMPLATE_FILE_WRITE=true")
        print("python3 scripts/astraa_env_template_writer.py")
    else:
        if not is_safe_template_path(ENV_FILE):
            raise SystemExit("❌ Refusing to write outside deployment_templates/")

        TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        ENV_FILE.write_text(ENV_TEMPLATE, encoding="utf-8")
        print(f"WROTE: {ENV_FILE}")

    section("SAFETY CONFIRMATION")
    print("This script did not write real secrets.")
    print("This script did not write to /etc.")
    print("This script did not modify system files.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
