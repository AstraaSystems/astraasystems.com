#!/usr/bin/env python3
"""
Astraa WSGI / Deployment Inventory

READ-ONLY SCRIPT.

Purpose:
- Inventory current deployment readiness before creating WSGI/deployment files.
- Locate:
  - Flask app creation
  - app.run(...) / development server startup
  - if __name__ == "__main__" block
  - existing wsgi.py / gunicorn / Procfile / runtime / systemd / nginx files
  - requirements files
  - environment-variable usage relevant to production deployment

Does NOT:
- modify api.py
- create deployment files
- start services
- deploy anything
- change secrets
"""

from __future__ import annotations

from pathlib import Path
import json
import re
from collections import Counter


ROOT = Path(".")
API_PATH = Path("api.py")

SCAN_FILES = [
    "api.py",
    "wsgi.py",
    "requirements.txt",
    "requirements-prod.txt",
    "Procfile",
    "runtime.txt",
    "gunicorn.conf.py",
    "Dockerfile",
    "docker-compose.yml",
    "nginx.conf",
    "astraa-api.service",
    ".env",
    ".env.example",
]

PATTERNS = [
    "Flask(",
    "app =",
    "app.run",
    "if __name__",
    "__main__",
    "host=",
    "port=",
    "debug=",
    "gunicorn",
    "uwsgi",
    "wsgi",
    "Procfile",
    "runtime",
    "nginx",
    "systemd",
    "ASTRAA_PUBLIC_LAUNCH_MODE",
    "ASTRAA_REQUEST_GUARD_ENABLED",
    "ASTRAA_ALLOWED_ORIGINS",
    "ASTRAA_ALLOW_LOCALHOST_CORS",
    "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE",
    "MONERIS_ENV",
    "MONERIS_STORE_ID",
    "MONERIS_API_TOKEN",
    "MONERIS_CHECKOUT_ID",
    "os.getenv",
    "os.environ",
]

DEF_RE = re.compile(r'^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def context(lines, line_no, radius=2):
    start = max(1, line_no - radius)
    end = min(len(lines), line_no + radius)
    return [
        {
            "line": idx,
            "text": lines[idx - 1].rstrip(),
        }
        for idx in range(start, end + 1)
    ]


def scan_text_file(path: Path):
    if not path.exists() or not path.is_file():
        return {
            "exists": False,
            "matches": [],
            "functions": [],
        }

    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as exc:
        return {
            "exists": True,
            "error": str(exc),
            "matches": [],
            "functions": [],
        }

    matches = []
    functions = []

    for idx, line in enumerate(lines, 1):
        matched = [p for p in PATTERNS if p.lower() in line.lower()]
        if matched:
            matches.append({
                "file": str(path),
                "line": idx,
                "matched": matched,
                "text": line.rstrip(),
                "context": context(lines, idx, 1),
            })

        def_match = DEF_RE.match(line)
        if def_match:
            function_name = def_match.group(1)
            if (
                "run" in function_name.lower()
                or "start" in function_name.lower()
                or "health" in function_name.lower()
                or "config" in function_name.lower()
                or "env" in function_name.lower()
                or "cors" in function_name.lower()
            ):
                functions.append({
                    "file": str(path),
                    "line": idx,
                    "function": function_name,
                    "context": context(lines, idx, 1),
                })

    return {
        "exists": True,
        "matches": matches,
        "functions": functions,
    }


def main():
    section("ASTRAA WSGI / DEPLOYMENT INVENTORY")
    print("Mode: READ ONLY")
    print("Repository root:", ROOT.resolve())

    discovered_files = []
    missing_files = []
    all_matches = []
    all_functions = []

    section("DEPLOYMENT FILE PRESENCE")
    for file_name in SCAN_FILES:
        path = ROOT / file_name
        result = scan_text_file(path)

        if result.get("exists"):
            discovered_files.append(file_name)
            print(f"FOUND: {file_name}")
            all_matches.extend(result.get("matches", []))
            all_functions.extend(result.get("functions", []))

            if result.get("error"):
                print(f"  ⚠️ Could not scan: {result['error']}")
        else:
            missing_files.append(file_name)
            print(f"MISSING: {file_name}")

    section("SUMMARY")
    print("Files found:", len(discovered_files))
    print("Files missing:", len(missing_files))
    print("Pattern matches:", len(all_matches))
    print("Deployment-related functions:", len(all_functions))

    section("MATCHES BY PATTERN")
    counts = Counter()
    for item in all_matches:
        for pattern in item["matched"]:
            counts[pattern] += 1

    for pattern, count in counts.most_common():
        print(f"{pattern}: {count}")

    section("DEPLOYMENT-RELATED FUNCTIONS")
    if not all_functions:
        print("None")
    for item in all_functions:
        print(json.dumps(item, indent=2, sort_keys=True))

    section("DETAILED MATCHES")
    if not all_matches:
        print("None")
    for item in all_matches:
        print(json.dumps(item, indent=2, sort_keys=True))

    section("INVENTORY NOTES")
    print("- If api.py exposes app = Flask(...), a wsgi.py entrypoint can likely import app.")
    print("- If api.py contains app.run(...), that should remain local/internal QA only.")
    print("- If wsgi.py is missing, next safe step is to add a small WSGI entrypoint.")
    print("- If requirements.txt lacks gunicorn, add a deployment plan before modifying dependencies.")
    print("- Do not create systemd/nginx/production config until deployment target is chosen.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify api.py.")
    print("This script did not create deployment files.")
    print("This script did not start services.")
    print("This script did not deploy Astraa.")
    print("This script did not change secrets or data.")


if __name__ == "__main__":
    main()
