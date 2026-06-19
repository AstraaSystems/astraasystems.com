#!/usr/bin/env python3
"""
Astraa Staging DB Validation

READ-ONLY SCRIPT.
Validates a local staging SQLite DB if it exists.

Does NOT:
- create a database
- create tables
- create indexes
- migrate data
- modify files
- delete files

Purpose:
- Safely inspect astraa_data/astraa_staging.db after intentional staging DB creation.
- Exit cleanly if the staging DB has not been created yet.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT / "astraa_data" / "astraa_staging.db"
SQLITE_PATH = Path(os.getenv("ASTRAA_STAGING_SQLITE_PATH", str(DEFAULT_DB_PATH)))


EXPECTED_TABLES = [
    "accounts",
    "subscriptions",
    "usage_counters",
    "payments",
    "payment_events",
    "core_entities",
    "core_activity",
    "core_events",
    "core_vault_records",
    "event_logs",
]


EXPECTED_INDEX_PREFIXES = [
    "idx_accounts_",
    "idx_subscriptions_",
    "idx_usage_",
    "idx_payments_",
    "idx_payment_events_",
    "idx_core_entities_",
    "idx_core_activity_",
    "idx_core_events_",
    "idx_core_vault_",
    "idx_event_logs_",
]


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def is_safe_path(path: Path) -> bool:
    resolved = path.resolve()
    root = ROOT.resolve()

    if not str(resolved).startswith(str(root)):
        return False

    if resolved.suffix != ".db":
        return False

    unsafe = ["prod", "production", "live", "customer", "moneris"]
    return not any(marker in str(resolved).lower() for marker in unsafe)


def fetch_all(conn, sql):
    return conn.execute(sql).fetchall()


def main():
    section("ASTRAA STAGING DB VALIDATION")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("SQLite path:", SQLITE_PATH)

    if not is_safe_path(SQLITE_PATH):
        section("SAFETY BLOCK")
        print("Refusing to inspect path because it failed local staging safety checks.")
        print("No database was created or modified.")
        return

    if not SQLITE_PATH.exists():
        section("STAGING DB STATUS")
        print("Staging DB not created yet.")
        print("This is expected unless ASTRAA_ALLOW_STAGING_DB_CREATE=true was intentionally used.")
        section("READ-ONLY CONFIRMATION")
        print("This script did not create a database.")
        print("This script did not create tables.")
        print("This script did not create indexes.")
        print("This script did not migrate data.")
        print("This script did not modify files.")
        return

    conn = sqlite3.connect(str(SQLITE_PATH))
    try:
        section("TABLES")
        tables = [
            row[0] for row in fetch_all(
                conn,
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            )
        ]

        for table in tables:
            print(table)

        missing_tables = [t for t in EXPECTED_TABLES if t not in tables]

        section("TABLE VALIDATION")
        if missing_tables:
            print("Missing expected tables:")
            for table in missing_tables:
                print("-", table)
        else:
            print("All expected tables are present.")

        section("ROW COUNTS")
        for table in tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
                print(f"{table}: {count}")
            except Exception as exc:
                print(f"{table}: could not count rows ({exc})")

        section("INDEXES")
        indexes = [
            row[0] for row in fetch_all(
                conn,
                "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name;"
            )
        ]

        for index in indexes:
            print(index)

        section("INDEX VALIDATION")
        missing_prefixes = []
        for prefix in EXPECTED_INDEX_PREFIXES:
            if not any(index.startswith(prefix) for index in indexes):
                missing_prefixes.append(prefix)

        if missing_prefixes:
            print("Missing expected index families:")
            for prefix in missing_prefixes:
                print("-", prefix)
        else:
            print("All expected index families are present.")

        section("READ-ONLY CONFIRMATION")
        print("This script inspected metadata only.")
        print("This script did not create a database.")
        print("This script did not create tables.")
        print("This script did not create indexes.")
        print("This script did not migrate data.")
        print("This script did not modify files.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
