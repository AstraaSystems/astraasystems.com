#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Astraa FinOps Engine — Autonomous Billing, Invoicing & Financial Ops Core
#  File: astraa_finops.py
#===============================================================================

import time
import uuid
import sqlite3
import os
import numpy as np
from typing import Dict, Any, List, Optional

class AstraaFinOps:
    """
    Handles:
      • automated invoice generation
      • usage-based billing
      • tax computation
      • stochastic surcharge modeling
      • ledger integration
    """

    def __init__(self, db_name: str = "astraa_finops.db"):
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
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id TEXT PRIMARY KEY,
                    client TEXT NOT NULL,
                    subtotal REAL NOT NULL,
                    tax REAL NOT NULL,
                    total REAL NOT NULL,
                    metadata_json TEXT NOT NULL,
                    timestamp_epoch REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_records (
                    record_id TEXT PRIMARY KEY,
                    client TEXT NOT NULL,
                    units REAL NOT NULL,
                    rate REAL NOT NULL,
                    cost REAL NOT NULL,
                    timestamp_epoch REAL NOT NULL
                )
            """)

            conn.commit()

    #---------------------------------------------------------------------------
    #  STOCHASTIC SURCHARGE
    #---------------------------------------------------------------------------
    def _surcharge(self, base: float) -> float:
        noise = np.random.normal(0, base * 0.02)
        return max(0.0, base + noise)

    #---------------------------------------------------------------------------
    #  RECORD USAGE
    #---------------------------------------------------------------------------
    def record_usage(self, client: str, units: float, rate: float) -> str:
        cost = units * rate
        record_id = f"USG-{uuid.uuid4().hex[:10].upper()}"
        ts = time.time()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usage_records
                (record_id, client, units, rate, cost, timestamp_epoch)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (record_id, client, units, rate, cost, ts))
            conn.commit()

        return record_id

    #---------------------------------------------------------------------------
    #  COMPUTE BILLING SUBTOTAL
    #---------------------------------------------------------------------------
    def _compute_subtotal(self, client: str) -> float:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cost FROM usage_records
                WHERE client = ?
            """, (client,))
            rows = cursor.fetchall()

        base = sum(r[0] for r in rows)
        return self._surcharge(base)

    #---------------------------------------------------------------------------
    #  TAX COMPUTATION
    #---------------------------------------------------------------------------
    def _tax(self, amount: float, rate: float = 0.13) -> float:
        return amount * rate

    #---------------------------------------------------------------------------
    #  GENERATE INVOICE
    #---------------------------------------------------------------------------
    def generate_invoice(self, client: str) -> Dict[str, Any]:
        subtotal = self._compute_subtotal(client)
        tax = self._tax(subtotal)
        total = subtotal + tax

        invoice_id = f"INV-{uuid.uuid4().hex[:10].upper()}"
        ts = time.time()

        metadata = {
            "client": client,
            "subtotal": subtotal,
            "tax": tax,
            "total": total
        }

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO invoices
                (invoice_id, client, subtotal, tax, total, metadata_json, timestamp_epoch)
                VALUES (?, ?, ?, ?, ?, json(?), ?)
            """, (
                invoice_id,
                client,
                subtotal,
                tax,
                total,
                str(metadata),
                ts
            ))
            conn.commit()

        return {
            "invoice_id": invoice_id,
            "timestamp": ts,
            "client": client,
            "subtotal": float(subtotal),
            "tax": float(tax),
            "total": float(total)
        }

    #---------------------------------------------------------------------------
    #  RETRIEVE INVOICE
    #---------------------------------------------------------------------------
    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM invoices
                WHERE invoice_id = ?
            """, (invoice_id,))
            row = cursor.fetchone()

            return dict(row) if row else None

#===============================================================================
#  END OF FILE — astraa_finops.py
#===============================================================================
