#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Observability & Metrics Engine — Metrics, Traces & Event Streams
#  File: observability_metrics_engine.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, List, Optional

class ObservabilityMetricsEngine:
    """
    Provides:
      • metric counters & gauges
      • distributed trace spans
      • event stream ingestion
      • anomaly detection flags
      • export pipelines for dashboards
    """

    def __init__(self):
        self.metrics: Dict[str, float] = {}
        self.traces: Dict[str, Dict[str, Any]] = {}
        self.events: List[Dict[str, Any]] = []
        self.anomalies: List[Dict[str, Any]] = []
        self.telemetry: Dict[str, Any] = {
            "metrics_recorded": 0,
            "traces_started": 0,
            "traces_finished": 0,
            "events_ingested": 0,
            "anomalies_detected": 0
        }

    #---------------------------------------------------------------------------
    #  METRICS
    #---------------------------------------------------------------------------
    def gauge(self, name: str, value: float):
        self.metrics[name] = value
        self.telemetry["metrics_recorded"] += 1

    def increment(self, name: str, amount: float = 1.0):
        self.metrics[name] = self.metrics.get(name, 0.0) + amount
        self.telemetry["metrics_recorded"] += 1

    #---------------------------------------------------------------------------
    #  TRACING
    #---------------------------------------------------------------------------
    def start_trace(self, name: str) -> str:
        tid = f"TRC-{uuid.uuid4().hex[:10].upper()}"
        self.traces[tid] = {
            "id": tid,
            "name": name,
            "start": time.time(),
            "end": None,
            "duration": None,
            "meta": {}
        }
        self.telemetry["traces_started"] += 1
        return tid

    def end_trace(self, trace_id: str, meta: Dict[str, Any]):
        if trace_id not in self.traces:
            return
        tr = self.traces[trace_id]
        tr["end"] = time.time()
        tr["duration"] = tr["end"] - tr["start"]
        tr["meta"] = meta
        self.telemetry["traces_finished"] += 1

    #---------------------------------------------------------------------------
    #  EVENT STREAM
    #---------------------------------------------------------------------------
    def event(self, subsystem: str, message: str, meta: Dict[str, Any]):
        eid = f"EVT-{uuid.uuid4().hex[:10].upper()}"
        entry = {
            "id": eid,
            "subsystem": subsystem,
            "message": message,
            "meta": meta,
            "timestamp": time.time()
        }
        self.events.append(entry)
        self.telemetry["events_ingested"] += 1

    #---------------------------------------------------------------------------
    #  ANOMALY FLAG
    #---------------------------------------------------------------------------
    def anomaly(self, category: str, details: Dict[str, Any]):
        aid = f"ANM-{uuid.uuid4().hex[:10].upper()}"
        entry = {
            "id": aid,
            "category": category,
            "details": details,
            "timestamp": time.time()
        }
        self.anomalies.append(entry)
        self.telemetry["anomalies_detected"] += 1

    #---------------------------------------------------------------------------
    #  EXPORT SNAPSHOT
    #---------------------------------------------------------------------------
    def export(self) -> Dict[str, Any]:
        return {
            "export_id": f"OBS-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "metrics": self.metrics.copy(),
            "recent_events": self.events[-50:],
            "recent_traces": list(self.traces.values())[-20:],
            "anomalies": self.anomalies[-20:],
            "telemetry": self.telemetry
        }

    #---------------------------------------------------------------------------
    #  FULL SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"OBS-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "metrics": self.metrics,
            "traces": self.traces,
            "events": self.events,
            "anomalies": self.anomalies,
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — observability_metrics_engine.py
#===============================================================================
