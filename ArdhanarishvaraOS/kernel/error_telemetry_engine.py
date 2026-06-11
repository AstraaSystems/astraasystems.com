#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Error Telemetry Engine — Autonomous Error Capture, Classification & Analytics
#  File: error_telemetry_engine.py
#===============================================================================

import time
import uuid
import sqlite3
import os
import numpy as np
from typing import Dict, Any, Optional, List

class ErrorTelemetryEngine:
    """
    Captures and analyzes:
      • engine errors
      • routing failures
      • dispatch failures
      • workflow breakdowns
      • anomaly detection
      • severity scoring
    """

    def __init__(self, db_name: str = "error_telemetry.db"):
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
                CREATE TABLE IF NOT EXISTS telemetry (
                    error_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity REAL NOT NULL,
                    metadata_json TEXT NOT NULL,
                    timestamp_epoch REAL NOT NULL
                )
            """)

            conn.commit()

    #---------------------------------------------------------------------------
    #  SEVERITY MODEL
    #---------------------------------------------------------------------------
    def _severity(self, category: str, message: str) -> float:
        base = {
            "engine_failure": 0.8,
            "dispatch_failure": 0.6,
            "workflow_failure": 0.7,
            "routing_error": 0.5,
            "unknown": 0.3
        }.get(category, 0.3)

        noise = np.random.normal(0, 0.05)
        length_factor = min(0.2, len(message) / 5000)

        return max(0.0, min(1.0, base + noise + length_factor))

    #---------------------------------------------------------------------------
    #  RECORD ERROR
    #---------------------------------------------------------------------------
    def record(
        self,
        source: str,
        category: str,
        message: str,
        metadata: Dict[str, Any]
    ) -> str:

        sev = self._severity(category, message)
        error_id = f"ERR-{uuid.uuid4().hex[:10].upper()}"
        ts = time.time()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO telemetry
                (error_id, source, category, message, severity, metadata_json, timestamp_epoch)
                VALUES (?, ?, ?, ?, ?, json(?), ?)
            """, (
                error_id,
                source,
                category,
                message,
                sev,
                str(metadata),
                ts
            ))
            conn.commit()

        return error_id

    #---------------------------------------------------------------------------
    #  QUERY ERRORS
    #---------------------------------------------------------------------------
    def query(
        self,
        source: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        query = "SELECT * FROM telemetry WHERE 1=1"
        params = []

        if source:
            query += " AND source = ?"
            params.append(source)

        if category:
            query += " AND category = ?"
            params.append(category)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(r) for r in rows]

    #---------------------------------------------------------------------------
    #  SEVERITY ANALYTICS
    #---------------------------------------------------------------------------
    def severity_report(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT severity FROM telemetry")
            rows = cursor.fetchall()

        if not rows:
            return {"average_severity": 0.0, "count": 0}

        arr = np.array([r[0] for r in rows])
        return {
            "average_severity": float(arr.mean()),
            "max_severity": float(arr.max()),
            "min_severity": float(arr.min()),
            "count": len(arr)
        }

#===============================================================================
#  END OF FILE — error_telemetry_engine.py
#===============================================================================
