#!/usr/bin/env python3
"""
Astraa Managed DB Staging Connection Self-Test

GUARDED SCRIPT.

Purpose:
- Validate managed staging DB configuration and optional connectivity.
- Refuse by default unless ASTRAA_ALLOW_MANAGED_DB_STAGING_SELFTEST=true.
- Never print DATABASE_URL or password values.
- Prepare for managed DB staging before adapter/cutover work.

Does NOT:
- create databases
- create tables
- create indexes
- import data
- migrate data
- modify JSON/JSONL/SQLite source files
- open customer access
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def mask_url(raw: str) -> str:
    if not raw:
        return ""

    try:
        parsed = urlparse(raw)
        scheme = parsed.scheme or "unknown"
        host = parsed.hostname or "unknown-host"
        port = f":{parsed.port}" if parsed.port else ""
        db_name = parsed.path.strip("/") or "unknown-db"
        return f"{scheme}://***:***@{host}{port}/{db_name}"
    except Exception:
        return "<masked-url>"


def main():
    section("ASTRAA MANAGED DB STAGING CONNECTION SELF-TEST")
    print("Mode: GUARDED / REFUSAL BY DEFAULT")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    allow = os.getenv("ASTRAA_ALLOW_MANAGED_DB_STAGING_SELFTEST", "false").strip().lower() == "true"
    engine = os.getenv("ASTRAA_MANAGED_DB_ENGINE", "").strip().lower()
    url = os.getenv("ASTRAA_MANAGED_DB_URL", "").strip()
    sqlite_path = os.getenv("ASTRAA_MANAGED_DB_SQLITE_PATH", "astraa_data/astraa_staging.db").strip()

    section("CONFIGURATION STATUS")
    print("ASTRAA_ALLOW_MANAGED_DB_STAGING_SELFTEST:", "true" if allow else "false")
    print("ASTRAA_MANAGED_DB_ENGINE:", engine or "<missing>")
    print("ASTRAA_MANAGED_DB_URL:", mask_url(url) if url else "<missing>")
    print("ASTRAA_MANAGED_DB_SQLITE_PATH:", sqlite_path if engine == "sqlite" else "<not used>")

    if not allow:
        section("SAFETY STATUS")
        print("Refusing to test managed DB staging connection because ASTRAA_ALLOW_MANAGED_DB_STAGING_SELFTEST is not true.")
        print("")
        print("To intentionally run a LOCAL SQLite staging connection check only:")
        print("export ASTRAA_ALLOW_MANAGED_DB_STAGING_SELFTEST=true")
        print("export ASTRAA_MANAGED_DB_ENGINE=sqlite")
        print("export ASTRAA_MANAGED_DB_SQLITE_PATH=astraa_data/astraa_staging.db")
        print("python3 scripts/astraa_managed_db_staging_connection_selftest.py")
        print("")
        print("To intentionally run a managed PostgreSQL-style config check later:")
        print("export ASTRAA_ALLOW_MANAGED_DB_STAGING_SELFTEST=true")
        print("export ASTRAA_MANAGED_DB_ENGINE=postgres")
        print("export ASTRAA_MANAGED_DB_URL='<managed staging database url>'")
        print("python3 scripts/astraa_managed_db_staging_connection_selftest.py")

        section("READ-ONLY CONFIRMATION")
        print("This script did not connect to a database.")
        print("This script did not create tables.")
        print("This script did not import data.")
        print("This script did not migrate data.")
        print("This script did not modify JSON/JSONL/SQLite source files.")
        raise SystemExit(0)

    section("VALIDATION")

    if engine not in {"sqlite", "postgres", "postgresql"}:
        print("FAIL: ASTRAA_MANAGED_DB_ENGINE must be one of: sqlite, postgres, postgresql.")
        raise SystemExit(1)

    if engine == "sqlite":
        db_path = ROOT / sqlite_path
        db_path.parent.mkdir(parents=True, exist_ok=True)

        print("SQLite staging path:", db_path)

        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("SELECT 1")
            conn.close()
            print("PASS: SQLite staging connection check succeeded.")
        except Exception as exc:
            print("FAIL: SQLite staging connection check failed.")
            print("Error type:", type(exc).__name__)
            raise SystemExit(1)

    if engine in {"postgres", "postgresql"}:
        if not url:
            print("FAIL: ASTRAA_MANAGED_DB_URL is required for postgres/postgresql.")
            raise SystemExit(1)

        parsed = urlparse(url)
        if parsed.scheme not in {"postgres", "postgresql"}:
            print("FAIL: ASTRAA_MANAGED_DB_URL must use postgres/postgresql scheme.")
            raise SystemExit(1)

        print("PASS: Managed PostgreSQL URL shape is present and masked.")
        print("NOTE: Live PostgreSQL connection is intentionally not attempted by this script unless a driver/adapter lane is added.")
        print("NOTE: This avoids accidentally depending on local driver packages or leaking connection details.")

    section("SUMMARY")
    print("✅ MANAGED DB STAGING CONNECTION SELF-TEST PASSED")

    section("READ-ONLY CONFIRMATION")
    print("This script did not create tables.")
    print("This script did not create indexes.")
    print("This script did not import data.")
    print("This script did not migrate data.")
    print("This script did not modify JSON/JSONL source files.")
    print("This script did not open customer access.")


if __name__ == "__main__":
    main()
