#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  AI Memory Engine — Autonomous Context Retention & Semantic Recall Core
#  File: ai_memory_engine.py
#===============================================================================

import time
import uuid
import sqlite3
import os
import numpy as np
from typing import Dict, Any, List, Optional

class AIMemoryEngine:
    """
    Handles:
      • semantic memory storage
      • weighted recall
      • relevance scoring
      • temporal decay
      • stochastic reinforcement
    """

    def __init__(self, db_name: str = "ai_memory.db"):
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
                CREATE TABLE IF NOT EXISTS memory (
                    memory_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    strength REAL NOT NULL,
                    timestamp_epoch REAL NOT NULL
                )
            """)

            conn.commit()

    #---------------------------------------------------------------------------
    #  TEMPORAL DECAY
    #---------------------------------------------------------------------------
    def _decay(self, strength: float, age: float) -> float:
        return max(0.0, strength * np.exp(-age / 86400))

    #---------------------------------------------------------------------------
    #  STOCHASTIC REINFORCEMENT
    #---------------------------------------------------------------------------
    def _reinforce(self, strength: float) -> float:
        noise = np.random.normal(0, 0.05)
        return max(0.0, min(1.0, strength + noise))

    #---------------------------------------------------------------------------
    #  STORE MEMORY
    #---------------------------------------------------------------------------
    def store(self, topic: str, content: str, strength: float = 0.5) -> str:
        mem_id = f"MEM-{uuid.uuid4().hex[:10].upper()}"
        ts = time.time()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memory
                (memory_id, topic, content, strength, timestamp_epoch)
                VALUES (?, ?, ?, ?, ?)
            """, (mem_id, topic, content, strength, ts))
            conn.commit()

        return mem_id

    #---------------------------------------------------------------------------
    #  RECALL MEMORY
    #---------------------------------------------------------------------------
    def recall(self, topic: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM memory
                WHERE topic = ?
            """, (topic,))
            rows = cursor.fetchall()

        now = time.time()
        results = []

        for r in rows:
            age = now - r["timestamp_epoch"]
            decayed = self._decay(r["strength"], age)
            reinforced = self._reinforce(decayed)

            results.append({
                "memory_id": r["memory_id"],
                "topic": r["topic"],
                "content": r["content"],
                "strength": float(reinforced),
                "timestamp": r["timestamp_epoch"]
            })

        results.sort(key=lambda x: x["strength"], reverse=True)
        return results

    #---------------------------------------------------------------------------
    #  DELETE MEMORY
    #---------------------------------------------------------------------------
    def delete(self, memory_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memory WHERE memory_id = ?", (memory_id,))
            conn.commit()

    #---------------------------------------------------------------------------
    #  FULL MEMORY DUMP
    #---------------------------------------------------------------------------
    def dump(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memory")
            rows = cursor.fetchall()

        return [dict(r) for r in rows]

#===============================================================================
#  END OF FILE — ai_memory_engine.py
#===============================================================================
