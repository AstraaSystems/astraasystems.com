#!/usr/bin/env python3
"""
Astraa Staging DB Row Inspector

READ-ONLY SCRIPT.

Purpose:
- Inspect actual rows in local staging SQLite DB.
- Confirm proof-only staging import contents.
- Show safe summaries of imported rows.

Does NOT:
- create a database
- create tables
- create indexes
- insert records
- update records
- delete records
- migrate data
- modify JSON/JSONL source files
"""

from __future__ import annotations

import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT / "astraa_data" / "astraa_staging.db"
SQLITE_PATH = Path(os.getenv("ASTRAA_STAGING_SQLITE_PATH", str(DEFAULT_DB_PATH)))

TABLES_TO_INSPECT = [
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

SENSITIVE_COLUMNS = {
    "idempotency_key",
    "ticket_reference",
    "safe_gateway_reference",
}


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

    unsafe_markers = [
        "prod",
        "production",
        "live",
        "customer",
        "moneris",
    ]

    return not any(marker in str(resolved).lower() for marker in unsafe_markers)


def mask_value(column, value):
    if value is None:
        return None

    if column not in SENSITIVE_COLUMNS:
        return value

    text = str(value)

    if len(text) <= 8:
        return "***"

    return text[:4] + "..." + text[-4:]


def fetch_table_names(conn):
    return [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        ).fetchall()
    ]


def fetch_columns(conn, table):
    return [
        row[1]
        for row in conn.execute(f"PRAGMA table_info({table});").fetchall()
    ]


def fetch_rows(conn, table, limit=10):
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM {table} LIMIT ?;", (limit,)).fetchall()
    return [dict(row) for row in rows]


def safe_row(row):
    return {
        key: mask_value(key, value)
        for key, value in row.items()
    }


def inspect_table(conn, table):
    section(f"TABLE: {table}")

    count = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
    print("Row count:", count)

    columns = fetch_columns(conn, table)
    print("Columns:")
    for column in columns:
        print("-", column)

    if count == 0:
        print("\nNo rows to inspect.")
        return

    rows = fetch_rows(conn, table, limit=10)

    print("\nSample rows:")
    for row in rows:
        print(json.dumps(safe_row(row), indent=2, sort_keys=True))


def main():
    section("ASTRAA STAGING DB ROW INSPECTOR")
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
        print("Run the guarded create template intentionally before inspecting rows.")
        section("READ-ONLY CONFIRMATION")
        print("This script did not create a database.")
        print("This script did not modify files.")
        return

    conn = sqlite3.connect(str(SQLITE_PATH))
    try:
        section("DATABASE TABLE SUMMARY")
        tables = fetch_table_names(conn)

        for table in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
            print(f"{table}: {count}")

        missing = [table for table in TABLES_TO_INSPECT if table not in tables]

        if missing:
            section("MISSING EXPECTED TABLES")
            for table in missing:
                print("-", table)

        for table in TABLES_TO_INSPECT:
            if table in tables:
                inspect_table(conn, table)

        section("READ-ONLY CONFIRMATION")
        print("This script inspected rows only.")
        print("This script did not create a database.")
        print("This script did not create tables.")
        print("This script did not create indexes.")
        print("This script did not insert records.")
        print("This script did not update records.")
        print("This script did not delete records.")
        print("This script did not modify JSON/JSONL source files.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
