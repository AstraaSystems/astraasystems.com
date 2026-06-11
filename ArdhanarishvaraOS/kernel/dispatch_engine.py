#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Dispatch Engine — Autonomous Multi‑Engine Task Distribution Core
#  File: dispatch_engine.py
#===============================================================================

import time
import uuid
import asyncio
import random
from typing import Dict, Any, Callable, Optional, List

class DispatchEngine:
    """
    Routes tasks, jobs, and workloads across ARKA engines using:
      • weighted dispatching
      • latency‑aware selection
      • stochastic load balancing
      • supervisor‑linked failure recovery
    """

    def __init__(self):
        self.engines: Dict[str, Callable[..., Any]] = {}
        self.weights: Dict[str, float] = {}
        self.latency: Dict[str, float] = {}
        self.supervisor: Optional[Callable[..., Any]] = None

    #---------------------------------------------------------------------------
    #  ENGINE REGISTRATION
    #---------------------------------------------------------------------------
    def register_engine(self, name: str, handler: Callable[..., Any], weight: float = 1.0):
        self.engines[name] = handler
        self.weights[name] = weight
        self.latency[name] = 0.1
        self._normalize()

    #---------------------------------------------------------------------------
    #  SUPERVISOR LINK
    #---------------------------------------------------------------------------
    def attach_supervisor(self, handler: Callable[..., Any]):
        self.supervisor = handler

    #---------------------------------------------------------------------------
    #  NORMALIZE WEIGHTS
    #---------------------------------------------------------------------------
    def _normalize(self):
        total = sum(self.weights.values())
        if total == 0:
            self.weights = {k: 0 for k in self.weights}
        else:
            self.weights = {k: v / total for k, v in self.weights.items()}

    #---------------------------------------------------------------------------
    #  ENGINE SELECTION
    #---------------------------------------------------------------------------
    def _select_engine(self) -> Optional[str]:
        if not self.engines:
            return None

        keys = list(self.engines.keys())
        vals = list(self.weights.values())

        # Latency‑aware stochastic selection
        adjusted = []
        for k, w in zip(keys, vals):
            l = self.latency.get(k, 0.1)
            adj = max(0.0001, w / (1 + l))
            adjusted.append(adj)

        total = sum(adjusted)
        probs = [a / total for a in adjusted]

        return random.choices(keys, weights=probs, k=1)[0]

    #---------------------------------------------------------------------------
    #  DISPATCH TASK
    #---------------------------------------------------------------------------
    async def dispatch(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        engine = self._select_engine()

        if not engine:
            return {
                "dispatch_id": f"DSP-{uuid.uuid4().hex[:10].upper()}",
                "status": "no_engine_available",
                "timestamp": time.time()
            }

        start = time.time()

        try:
            result = await self.engines[engine](task, payload)
            self.latency[engine] = (self.latency[engine] + (time.time() - start)) / 2

            return {
                "dispatch_id": f"DSP-{uuid.uuid4().hex[:10].upper()}",
                "engine": engine,
                "status": "ok",
                "result": result,
                "timestamp": time.time()
            }

        except Exception as e:
            self.latency[engine] *= 1.5

            if self.supervisor:
                await self.supervisor("dispatch_failure", {"engine": engine, "error": str(e)})

            return {
                "dispatch_id": f"DSP-{uuid.uuid4().hex[:10].upper()}",
                "engine": engine,
                "status": "engine_error",
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  BULK DISPATCH
    #---------------------------------------------------------------------------
    async def dispatch_bulk(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for t in tasks:
            r = await self.dispatch(t["task"], t["payload"])
            results.append(r)
        return results

#===============================================================================
#  END OF FILE — dispatch_engine.py
#===============================================================================
