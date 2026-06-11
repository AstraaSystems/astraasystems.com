#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Kernel Telemetry Engine — Metrics, Events & Health Core
#  File: kernel_telemetry_engine.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, List

class KernelTelemetryEngine:
    """
    Provides:
      • kernel event ingestion
      • metric counters & gauges
      • subsystem health scoring
      • time-series telemetry logs
      • exportable telemetry packets
    """

    def __init__(self):
        self.metrics: Dict[str, float] = {}
        self.events: List[Dict[str, Any]] = []
        self.health: Dict[str, str] = {}
        self.snapshots: List[Dict[str, Any]] = []

    #---------------------------------------------------------------------------
    #  RECORD METRIC
    #---------------------------------------------------------------------------
    def metric(self, name: str, value: float):
        self.metrics[name] = value

    #---------------------------------------------------------------------------
    #  INCREMENT METRIC
    #---------------------------------------------------------------------------
    def increment(self, name: str, amount: float = 1.0):
        self.metrics[name] = self.metrics.get(name, 0.0) + amount

    #---------------------------------------------------------------------------
    #  RECORD EVENT
    #---------------------------------------------------------------------------
    def event(self, subsystem: str, message: str, meta: Dict[str, Any]):
        entry = {
            "event_id": f"EVT-{uuid.uuid4().hex[:10].upper()}",
            "subsystem": subsystem,
            "message": message,
            "meta": meta,
            "timestamp": time.time()
        }
        self.events.append(entry)

    #---------------------------------------------------------------------------
    #  SET HEALTH STATUS
    #---------------------------------------------------------------------------
    def set_health(self, subsystem: str, status: str):
        self.health[subsystem] = status

    #---------------------------------------------------------------------------
    #  EXPORT TELEMETRY PACKET
    #---------------------------------------------------------------------------
    def export(self) -> Dict[str, Any]:
        packet = {
            "packet_id": f"TLM-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "metrics": self.metrics.copy(),
            "events": self.events[-50:],  # last 50 events
            "health": self.health.copy()
        }
        self.snapshots.append(packet)
        return packet

    #---------------------------------------------------------------------------
    #  FULL SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"TLS-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "metrics": self.metrics,
            "events": self.events,
            "health": self.health,
            "snapshots": len(self.snapshots)
        }

#===============================================================================
#  END OF FILE — kernel_telemetry_engine.py
#===============================================================================
