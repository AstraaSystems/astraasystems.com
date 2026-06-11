#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Sovereign Ledger Engine — Immutable Financial Event Store
#  File: ledger.py
#===============================================================================

import os
import time
import uuid
import sqlite3
from typing import Dict, Any, List, Optional

class SovereignLedger:
    """
    Immutable financial ledger for ARKA Pillai Holdings.
    """

    def __init__(self, db_name: str = "sovereign_ledger.db"):
        self.db_path = os.path.join(
            os.getenv("SOVEREIGN_DATA_DIR", "./"),
            db_name
        )
        self._bootstrap_schema()

    #---------------------------------------------------------------------------
    #  SCHEMA INITIALIZATION
    #---------------------------------------------------------------------------
    def _bootstrap_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ledger_events (
                    entry_id TEXT PRIMARY KEY,
                    source_engine TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    timestamp_epoch REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ledger_balances (
                    account_key TEXT PRIMARY KEY,
                    balance REAL NOT NULL,
                    currency TEXT NOT NULL,
                    last_update REAL NOT NULL
                )
            """)

            conn.commit()

    #---------------------------------------------------------------------------
    #  LEDGER ENTRY CREATION
    #---------------------------------------------------------------------------
    def record_event(
        self,
        source: str,
        event_type: str,
        amount: float,
        currency: str,
        metadata: Dict[str, Any]
    ) -> str:
        entry_id = f"LED-{uuid.uuid4().hex[:12].upper()}"
        ts = time.time()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ledger_events
                (entry_id, source_engine, event_type, amount, currency,
                 metadata_json, timestamp_epoch)
                VALUES (?, ?, ?, ?, ?, json(?), ?)
            """, (
                entry_id,
                source,
                event_type,
                amount,
                currency,
                str(metadata),
                ts
            ))
            conn.commit()

        return entry_id

    #---------------------------------------------------------------------------
    #  BALANCE UPDATE
    #---------------------------------------------------------------------------
    def update_balance(self, account: str, delta: float, currency: str):
        now = time.time()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT balance FROM ledger_balances
                WHERE account_key = ?
            """, (account,))
            row = cursor.fetchone()

            if row is None:
                cursor.execute("""
                    INSERT INTO ledger_balances
                    (account_key, balance, currency, last_update)
                    VALUES (?, ?, ?, ?)
                """, (account, delta, currency, now))
            else:
                new_balance = row[0] + delta
                cursor.execute("""
                    UPDATE ledger_balances
                    SET balance = ?, last_update = ?
                    WHERE account_key = ?
                """, (new_balance, now, account))

            conn.commit()

    #---------------------------------------------------------------------------
    #  BALANCE RETRIEVAL
    #---------------------------------------------------------------------------
    def get_balance(self, account: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM ledger_balances
                WHERE account_key = ?
            """, (account,))
            row = cursor.fetchone()

            return dict(row) if row else None

    #---------------------------------------------------------------------------
    #  EVENT QUERY
    #---------------------------------------------------------------------------
    def query_events(
        self,
        source: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM ledger_events WHERE 1=1"
        params = []

        if source:
            query += " AND source_engine = ?"
            params.append(source)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(r) for r in rows]

#===============================================================================
#  END OF FILE — ledger.py
#===============================================================================
