#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Sovereign Circuit Breaker — Autonomous Failure Containment Layer
#  File: circuit_breaker.py
#===============================================================================

import time
import os
import sqlite3
import uuid
from typing import Dict, Any, Optional

class SovereignCircuitBreaker:
    """
    Autonomous circuit breaker for all ARKA external operations.
    """

    def __init__(
        self,
        db_name: str = "sovereign_breaker.db",
        failure_threshold: int = 5,
        cooldown_window: int = 45
    ):
        self.db_path = os.path.join(
            os.getenv("SOVEREIGN_DATA_DIR", "./"),
            db_name
        )
        self.failure_threshold = failure_threshold
        self.cooldown_window = cooldown_window
        self._bootstrap_schema()

    def _bootstrap_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS breaker_registry (
                    endpoint_key TEXT PRIMARY KEY,
                    failure_count INTEGER DEFAULT 0,
                    breaker_state TEXT DEFAULT 'CLOSED',
                    last_failure_epoch REAL DEFAULT 0,
                    last_state_change REAL DEFAULT 0
                )
            """)
            conn.commit()

    def _get_row(self, endpoint: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM breaker_registry WHERE endpoint_key = ?",
                (endpoint,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def _init_endpoint(self, endpoint: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO breaker_registry
                (endpoint_key, failure_count, breaker_state,
                 last_failure_epoch, last_state_change)
                VALUES (?, 0, 'CLOSED', 0, ?)
            """, (endpoint, time.time()))
            conn.commit()

    def is_request_allowed(self, endpoint: str) -> bool:
        self._init_endpoint(endpoint)
        row = self._get_row(endpoint)

        state = row["breaker_state"]
        last_failure = row["last_failure_epoch"]

        if state == "OPEN":
            if time.time() - last_failure >= self.cooldown_window:
                self._set_state(endpoint, "HALF_OPEN")
                return True
            return False

        return True

    def register_failure(self, endpoint: str):
        self._init_endpoint(endpoint)
        row = self._get_row(endpoint)

        new_count = row["failure_count"] + 1
        now = time.time()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE breaker_registry
                SET failure_count = ?, last_failure_epoch = ?
                WHERE endpoint_key = ?
            """, (new_count, now, endpoint))
            conn.commit()

        if new_count >= self.failure_threshold:
            self._set_state(endpoint, "OPEN")

    def register_success(self, endpoint: str):
        self._init_endpoint(endpoint)
        row = self._get_row(endpoint)

        if row["breaker_state"] == "HALF_OPEN":
            self._set_state(endpoint, "CLOSED")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE breaker_registry
                SET failure_count = 0
                WHERE endpoint_key = ?
            """, (endpoint,))
            conn.commit()

    def _set_state(self, endpoint: str, new_state: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE breaker_registry
                SET breaker_state = ?, last_state_change = ?
                WHERE endpoint_key = ?
            """, (new_state, time.time(), endpoint))
            conn.commit()

    def get_status(self, endpoint: str) -> Dict[str, Any]:
        self._init_endpoint(endpoint)
        return self._get_row(endpoint)

#===============================================================================
#  END OF FILE — circuit_breaker.py
#===============================================================================
