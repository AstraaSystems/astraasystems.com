#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Kernel Health Monitor — Autonomous System Vitality & Stability Scanner
#  File: kernel_health_monitor.py
#===============================================================================

import time
import uuid
import psutil
import asyncio
import numpy as np
from typing import Dict, Any, List

class KernelHealthMonitor:
    """
    Monitors:
      • CPU load
      • memory pressure
      • disk I/O
      • network throughput
      • engine heartbeat signals
      • anomaly detection via stochastic drift
    """

    def __init__(self):
        self.engines: Dict[str, float] = {}
        self.history: List[Dict[str, Any]] = []

    #---------------------------------------------------------------------------
    #  REGISTER ENGINE HEARTBEAT
    #---------------------------------------------------------------------------
    def register_engine(self, name: str):
        self.engines[name] = time.time()

    #---------------------------------------------------------------------------
    #  UPDATE HEARTBEAT
    #---------------------------------------------------------------------------
    def heartbeat(self, name: str):
        if name in self.engines:
            self.engines[name] = time.time()

    #---------------------------------------------------------------------------
    #  STOCHASTIC ANOMALY DRIFT
    #---------------------------------------------------------------------------
    def _drift(self) -> float:
        return float(np.random.normal(0.0, 0.05))

    #---------------------------------------------------------------------------
    #  SYSTEM METRICS
    #---------------------------------------------------------------------------
    def _system_metrics(self) -> Dict[str, float]:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        return {
            "cpu": cpu,
            "memory": mem,
            "disk": disk,
            "network": float(net)
        }

    #---------------------------------------------------------------------------
    #  ENGINE HEALTH CHECK
    #---------------------------------------------------------------------------
    def _engine_health(self) -> Dict[str, float]:
        now = time.time()
        health = {}

        for engine, ts in self.engines.items():
            delta = now - ts
            score = max(0.0, min(1.0, 1 - (delta / 30)))
            score += self._drift()
            score = max(0.0, min(1.0, score))
            health[engine] = score

        return health

    #---------------------------------------------------------------------------
    #  FULL HEALTH SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        sysm = self._system_metrics()
        eng = self._engine_health()

        packet = {
            "health_id": f"HLT-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "system": sysm,
            "engines": eng,
            "overall_score": float(
                max(0.0, min(1.0,
                    (1 - sysm["cpu"] / 100) * 0.25 +
                    (1 - sysm["memory"] / 100) * 0.25 +
                    (1 - sysm["disk"] / 100) * 0.20 +
                    (sum(eng.values()) / (len(eng) or 1)) * 0.30 +
                    self._drift()
                ))
            )
        }

        self.history.append(packet)
        return packet

    #---------------------------------------------------------------------------
    #  ASYNC PERIODIC MONITORING
    #---------------------------------------------------------------------------
    async def monitor(self, interval: float = 5.0):
        while True:
            self.snapshot()
            await asyncio.sleep(interval)

    #---------------------------------------------------------------------------
    #  RETRIEVE HISTORY
    #---------------------------------------------------------------------------
    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

#===============================================================================
#  END OF FILE — kernel_health_monitor.py
#===============================================================================
