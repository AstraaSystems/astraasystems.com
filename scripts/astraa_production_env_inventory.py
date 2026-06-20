#!/usr/bin/env python3
"""
Astraa Production Environment / Secrets Inventory

READ-ONLY SCRIPT.

Purpose:
- Inventory environment variables and secret-related references before deployment.
- Identify production-required variables.
- Check common local files for secret placeholders or accidental secret-looking values.
- Prepare for secure environment/secret manager setup.

Does NOT:
- print actual environment variable values
- modify files
- create .env files
- change secrets
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
import re
import json
from collections import Counter
from datetime import datetime, timezone


ROOT = Path(".")
SCAN_FILES = [
    "api.py",
    "wsgi.py",
    "requirements.txt",
    ".env",
    ".env.example",
    "deployment_templates/astraa-api.env.template",
]

ENV_PATTERN = re.compile(r'os\.getenv\(["\']([^"\']+)["\']')
ENVIRON_PATTERN = re.compile(r'os\.environ(?:\.get)?\(["\']([^"\']+)["\']')

SECRET_KEYWORDS = [
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "API_KEY",
    "API_TOKEN",
    "CHECKOUT_ID",
    "STORE_ID",
    "MONERIS",
]

REQUIRED_PRODUCTION_ENV = [
    "ASTRAA_PUBLIC_LAUNCH_MODE",
    "ASTRAA_REQUEST_GUARD_ENABLED",
    "ASTRAA_ALLOWED_ORIGINS",
    "ASTRAA_ALLOW_LOCALHOST_CORS",
    "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE",
    "ASTRAA_STORAGE_BACKEND",
    "MONERIS_ENV",
    "MONERIS_STORE_ID",
    "MONERIS_API_TOKEN",
    "MONERIS_CHECKOUT_ID",
    "ASTRAA_TEST_AMOUNT",
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def safe_preview_line(line):
    redacted = line
    for keyword in SECRET_KEYWORDS:
        if keyword.lower() in redacted.lower() and "=" in redacted:
            key = redacted.split("=", 1)[0]
            redacted = key + "=<REDACTED_OR_PLACEHOLDER>"
    return redacted.rstrip()


def scan_file(path):
    result = {
        "exists": path.exists(),
        "env_refs": [],
        "secret_keyword_lines": [],
    }

    if not path.exists() or not path.is_file():
        return result

    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as exc:
        result["error"] = str(exc)
        return result

    for idx, line in enumerate(lines, 1):
        for match in ENV_PATTERN.findall(line):
            result["env_refs"].append({
                "line": idx,
                "name": match,
                "text": safe_preview_line(line),
            })

        for match in ENVIRON_PATTERN.findall(line):
            result["env_refs"].append({
                "line": idx,
                "name": match,
                "text": safe_preview_line(line),
            })

        if any(keyword.lower() in line.lower() for keyword in SECRET_KEYWORDS):
            result["secret_keyword_lines"].append({
                "line": idx,
                "text": safe_preview_line(line),
            })

    return result


def main():
    section("ASTRAA PRODUCTION ENVIRONMENT / SECRETS INVENTORY")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Repository root:", ROOT.resolve())

    all_env_refs = []
    all_secret_lines = []

    section("FILE INVENTORY")
    for file_name in SCAN_FILES:
        path = ROOT / file_name
        result = scan_file(path)

        if result.get("exists"):
            print(f"FOUND: {file_name}")
        else:
            print(f"MISSING: {file_name}")

        if result.get("error"):
            print("  ERROR:", result["error"])

        for ref in result.get("env_refs", []):
            ref["file"] = file_name
            all_env_refs.append(ref)

        for item in result.get("secret_keyword_lines", []):
            item["file"] = file_name
            all_secret_lines.append(item)

    section("ENVIRONMENT REFERENCES FOUND")
    if not all_env_refs:
        print("None")
    else:
        counts = Counter(ref["name"] for ref in all_env_refs)
        for name, count in counts.most_common():
            print(f"{name}: {count}")

    section("REQUIRED PRODUCTION ENV CHECKLIST")
    found_names = {ref["name"] for ref in all_env_refs}

    for name in REQUIRED_PRODUCTION_ENV:
        status = "REFERENCED" if name in found_names else "NOT FOUND IN CODE SCAN"
        print(f"{name}: {status}")

    section("SECRET-RELATED LINES / REDACTED PREVIEW")
    if not all_secret_lines:
        print("None")
    else:
        for item in all_secret_lines:
            print(json.dumps(item, indent=2, sort_keys=True))

    section("DEPLOYMENT SECRET RULES")
    print("- Do not commit real Moneris credentials.")
    print("- Production secrets should come from server environment or secret manager.")
    print("- .env may be used locally only if excluded from public exposure and never committed with real secrets.")
    print("- Deployment templates should contain placeholders only.")
    print("- Logs should not print raw secret values.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not print actual environment values.")
    print("This script did not modify files.")
    print("This script did not create .env files.")
    print("This script did not change secrets.")
    print("This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
