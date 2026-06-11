#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  OS Routing Rules — Autonomous Multi‑Engine Request Router
#  File: os_routing_rules.py
#===============================================================================

import time
import uuid
import hashlib
from typing import Dict, Any, Callable, Optional

class OSRoutingRules:
    """
    Determines which ARKA engine handles which request based on:
      • request type
      • payload signature
      • routing weights
      • engine availability
      • supervisor feedback
    """

    def __init__(self):
        self.routes: Dict[str, str] = {}
        self.weights: Dict[str, float] = {}
        self.engines: Dict[str, Callable[..., Any]] = {}
        self.supervisor: Optional[Callable[..., Any]] = None

    #---------------------------------------------------------------------------
    #  ENGINE REGISTRATION
    #---------------------------------------------------------------------------
    def register_engine(self, name: str, handler: Callable[..., Any], weight: float = 1.0):
        self.engines[name] = handler
        self.weights[name] = weight
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
    #  SIGNATURE HASH
    #---------------------------------------------------------------------------
    def _sig(self, payload: Dict[str, Any]) -> str:
        raw = str(payload).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    #---------------------------------------------------------------------------
    #  ROUTE DECISION
    #---------------------------------------------------------------------------
    def _select_engine(self, request_type: str, payload: Dict[str, Any]) -> Optional[str]:
        if request_type in self.routes:
            return self.routes[request_type]

        sig = int(self._sig(payload), 16)
        keys = list(self.weights.keys())
        vals = list(self.weights.values())

        if not keys:
            return None

        idx = sig % len(keys)
        return keys[idx]

    #---------------------------------------------------------------------------
    #  ROUTE REQUEST
    #---------------------------------------------------------------------------
    async def route(self, request_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        engine = self._select_engine(request_type, payload)

        if not engine or engine not in self.engines:
            return {
                "route_id": f"RT-{uuid.uuid4().hex[:10].upper()}",
                "status": "no_engine_available",
                "timestamp": time.time()
            }

        try:
            result = await self.engines[engine](request_type, payload)
            return {
                "route_id": f"RT-{uuid.uuid4().hex[:10].upper()}",
                "engine": engine,
                "status": "ok",
                "result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            if self.supervisor:
                await self.supervisor("engine_failure", {"engine": engine, "error": str(e)})

            return {
                "route_id": f"RT-{uuid.uuid4().hex[:10].upper()}",
                "engine": engine,
                "status": "engine_error",
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  MANUAL ROUTE OVERRIDE
    #---------------------------------------------------------------------------
    def override(self, request_type: str, engine: str):
        if engine in self.engines:
            self.routes[request_type] = engine

#===============================================================================
#  END OF FILE — os_routing_rules.py
#===============================================================================
