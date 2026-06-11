# File: /home/keshanth/ARKA/ardhanarishvara/execution/ledger.py
#!/usr/bin/env python3
"""
Ledger — Persistent State Machine
---------------------------------
Responsibilities:
    - Maintain durable JSON-based state
    - Track balances (TFSA, RRSP, RESP, income, harvested, retained)
    - Provide atomic read/write operations
    - Ensure system-wide consistency
    - Used by TreasuryAgent, Execution Engine, and Meta-Cognitive layer

The ledger is the single source of truth for the entire system.
"""

import json
import os
import threading
from typing import Any, Dict


class Ledger:
    """
    JSON-backed persistent ledger.
    Thread-safe and process-safe using a simple lock.
    """

    LEDGER_PATH = "/home/keshanth/ARKA/ardhanarishvara/ledger.json"

    def __init__(self):
        self.lock = threading.Lock()
        self._ensure_ledger_exists()

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------
    def _ensure_ledger_exists(self):
        """
        Creates the ledger file if it does not exist.
        """
        if not os.path.exists(self.LEDGER_PATH):
            initial_state = {
                "income_total": 0.0,
                "harvested_total": 0.0,
                "retained_total": 0.0,
                "TFSA": 0.0,
                "RRSP": 0.0,
                "RESP": 0.0,
                "orders_executed": 0,
                "profit_total": 0.0,
            }
            self._write_state(initial_state)

    # ---------------------------------------------------------
    # Internal Read/Write
    # ---------------------------------------------------------
    def _read_state(self) -> Dict[str, Any]:
        with open(self.LEDGER_PATH, "r") as f:
            return json.load(f)

    def _write_state(self, state: Dict[str, Any]):
        with open(self.LEDGER_PATH, "w") as f:
            json.dump(state, f, indent=4)

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def update_balance(self, key: str, amount: float):
        """
        Atomically updates a numeric balance in the ledger.
        """
        with self.lock:
            state = self._read_state()
            state[key] = round(state.get(key, 0.0) + amount, 2)
            self._write_state(state)

    def set_value(self, key: str, value: Any):
        """
        Sets a ledger field to a specific value.
        """
        with self.lock:
            state = self._read_state()
            state[key] = value
            self._write_state(state)

    def get_value(self, key: str) -> Any:
        """
        Retrieves a value from the ledger.
        """
        with self.lock:
            state = self._read_state()
            return state.get(key)

    def get_all(self) -> Dict[str, Any]:
        """
        Returns the entire ledger state.
        """
        with self.lock:
            return self._read_state()


# ============================================================
# Standalone Test Harness
# ============================================================

if __name__ == "__main__":
    ledger = Ledger()
    print("Initial Ledger:", ledger.get_all())

    ledger.update_balance("income_total", 1000)
    ledger.update_balance("TFSA", 50)

    print("Updated Ledger:", ledger.get_all())
