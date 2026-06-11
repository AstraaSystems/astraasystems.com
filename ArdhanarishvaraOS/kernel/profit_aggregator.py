#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Profit Aggregator — Multi‑Engine Profit Collection + Consolidation Core
#  File: profit_aggregator.py
#===============================================================================

import time
import uuid
import numpy as np
from typing import Dict, Any, List

class ProfitAggregator:
    """
    Collects profit outputs from all ARKA engines and consolidates them into
    a unified profit packet for the Lux Profit Allocator.
    """

    def __init__(self):
        self.sources: Dict[str, float] = {}
        self.history: List[Dict[str, Any]] = []

    #---------------------------------------------------------------------------
    #  REGISTER ENGINE SOURCE
    #---------------------------------------------------------------------------
    def register_source(self, name: str):
        self.sources[name] = 0.0

    #---------------------------------------------------------------------------
    #  INGEST PROFIT FROM ENGINE
    #---------------------------------------------------------------------------
    def ingest(self, engine: str, amount: float):
        if engine not in self.sources:
            self.sources[engine] = 0.0
        self.sources[engine] += amount

    #---------------------------------------------------------------------------
    #  STOCHASTIC SMOOTHING
    #---------------------------------------------------------------------------
    def _smooth(self, values: List[float]) -> float:
        if not values:
            return 0.0
        arr = np.array(values)
        noise = np.random.normal(0, arr.mean() * 0.03)
        return max(0.0, arr.sum() + noise)

    #---------------------------------------------------------------------------
    #  CONSOLIDATE PROFITS
    #---------------------------------------------------------------------------
    def consolidate(self) -> Dict[str, Any]:
        engines = list(self.sources.keys())
        values = list(self.sources.values())

        total = self._smooth(values)

        packet = {
            "packet_id": f"AGG-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "engines": {k: float(v) for k, v in self.sources.items()},
            "total_profit": float(total)
        }

        self.history.append(packet)
        self.sources = {k: 0.0 for k in self.sources}

        return packet

    #---------------------------------------------------------------------------
    #  HISTORY RETRIEVAL
    #---------------------------------------------------------------------------
    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

#===============================================================================
#  END OF FILE — profit_aggregator.py
#===============================================================================
