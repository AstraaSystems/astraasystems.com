#!/usr/bin/env python3
from __future__ import annotations
import math
import random
from collections import deque
from typing import Dict, List, Optional, Tuple

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

    def normalize(self, x: float) -> float:
        std = math.sqrt(self.m2 / self.n) if self.n > 1 else 1.0
        return (x - self.mean) / (std + self.eps)

class EliteEstimator:
    def __init__(self, signal_names: List[str]):
        self.signal_names = signal_names
        self.normalizers = {name: OnlineNormalizer() for name in signal_names}
        self.state_estimate = 0.5
        self.confidence = 0.85

    def predict(self, signals: dict, scenario: str) -> dict:
        # Generate individual expert views
        # Fusion: Weighted aggregate of input signals
        fusion_val = sum(signals.values()) / len(signals)
        
        # Trend: Simple drift estimate (mocking the internal state)
        trend_val = fusion_val * 0.95 
        
        # History: Reference to previous actuals
        history_val = self.state_estimate
        
        # Calculate Consensus
        experts = {
            "fusion": fusion_val,
            "trend": trend_val,
            "history": history_val
        }
        
        # Simple weighted consensus (Equal weighting for now)
        prediction = sum(experts.values()) / len(experts)
        
        # Confidence calculation based on expert variance (lower variance = higher confidence)
        vals = list(experts.values())
        variance = max(vals) - min(vals)
        confidence = max(0.5, 1.0 - (variance * 0.5)) # Normalize variance impact
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "scenario": scenario,
            "experts": experts  # This is the diagnostic data
        }
    def update(self, actual: float) -> None:
        self.state_estimate = actual

class ArkaConstructionEstimator:
    def __init__(self):
        self.construction_signals = [
            "labour_hours", "material_cost_index", "equipment_cost",
            "site_complexity", "schedule_pressure", "region_factor",
            "historical_variance", "bid_competitiveness"
        ]
        self.engine = EliteEstimator(signal_names=self.construction_signals)

    def estimate(self, signals: dict, scenario: str):
        raw_pred = self.engine.predict(signals, scenario=scenario)
        confidence = raw_pred['confidence']

        if confidence >= 0.90:
            route = "AUTO_EXECUTE"
            action = "Proceed with bid/procurement"
        elif confidence >= 0.70:
            route = "CROSS_VALIDATE"
            action = "Flag for peer-review/senior validation"
        else:
            route = "ESCALATE"
            action = "Halt: Requires manual re-run and expert intervention"

        return {
            **raw_pred,
            "governance": {
                "route": route,
                "action": action,
                "bid_status": "APPROVED" if route == "AUTO_EXECUTE" else "PENDING"
            }
        }

    def update_actuals(self, actual_cost: float):
        return self.engine.update(actual=actual_cost)
class BidStrategist:
    def __init__(self, margin_target=0.15, risk_tolerance=0.5):
        self.margin_target = margin_target
        self.risk_tolerance = risk_tolerance

    def evaluate(self, estimate_result, market_conditions):
        cost = estimate_result["prediction"]
        # Strategic math: Cost + Margin + Risk-Adjusted Premium
        base_bid = cost * (1 + self.margin_target)
        risk_premium = market_conditions.get("volatility", 0.05) * self.risk_tolerance
        
        final_bid = base_bid * (1 + risk_premium)
        
        return {
            "bid_price": round(final_bid, 4),
            "suggested_margin": round(final_bid - cost, 4),
            "recommendation": "AGGRESSIVE" if cost < 0.5 else "CONSERVATIVE"
        }
