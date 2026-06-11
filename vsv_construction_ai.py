#!/usr/bin/env python3
"""
vsv_construction_ai.py

VSV Construction AI
===================
Construction-specific sovereign intelligence module for:
- Arka (executive controller)
- Ardhanarishvara OS (governance + orchestration)
- VSV Estimator (adaptive cost / difficulty prediction)
- Bid / No-Bid engine
- Margin advisor
- Capital allocator
- Portfolio intelligence
"""

from __future__ import annotations
import math, random
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Tuple

# =========================================================
# Utility layers
# =========================================================
class OnlineNormalizer:
    def __init__(self, eps: float = 1e-8):
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.eps = eps

    def update(self, x: float) -> None:
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.m2 += delta * delta2

    @property
    def std(self) -> float:
        return math.sqrt(self.m2 / self.n) if self.n > 1 else 1.0

    def normalize(self, x: float) -> float:
        return (x - self.mean) / (self.std + self.eps)

# =========================================================
# Core Systems
# =========================================================

class VSVEstimator:
    def __init__(self):
        self.normalizer = OnlineNormalizer()
        self.variance_buffer = deque(maxlen=50)

    def predict(self, signals: Dict[str, float]) -> float:
        # Simple weighted fusion for demo
        weights = {
            "labour_hours": 0.25, "material_cost_index": 0.2,
            "equipment_cost": 0.15, "site_complexity": 0.15,
            "schedule_pressure": 0.1, "region_factor": 0.1,
            "historical_variance": 0.05
        }
        score = sum(signals.get(k, 0.5) * w for k, w in weights.items())
        return max(0, min(1, score + random.uniform(-0.02, 0.02)))

class ArdhanarishvaraOS:
    def __init__(self, estimator):
        self.estimator = estimator
        self.portfolio = {"total_margin": 0.0, "risk": 0.0, "count": 0}

    def route_request(self, payload):
        prediction = self.estimator.predict(payload["signals"])
        return {
            "prediction": prediction,
            "status": "APPROVED" if prediction < 0.8 else "REVIEW_REQUIRED"
        }

    def snapshot(self):
        return {"portfolio_state": self.portfolio}

class Arka:
    def __init__(self, os_kernel):
        self.os = os_kernel

    def evaluate_project(self, payload):
        routing = self.os.route_request(payload)
        return {
            "project": payload["project_name"],
            "result": {
                "estimator": {"prediction": routing["prediction"]},
                "route": {"route": routing["status"]},
                "bid_decision": {"recommendation": "BID_SAFE" if routing["status"] == "APPROVED" else "BID_SELECTIVE"}
            }
        }

def build_system():
    estimator = VSVEstimator()
    os_kernel = ArdhanarishvaraOS(estimator)
    arka = Arka(os_kernel)
    return arka, os_kernel
