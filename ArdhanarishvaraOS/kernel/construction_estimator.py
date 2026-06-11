#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Construction Estimator — Autonomous Material, Labor & Cost Modeling Engine
#  File: construction_estimator.py
#===============================================================================

import time
import uuid
import numpy as np
from typing import Dict, Any, List

class ConstructionEstimator:
    """
    Computes construction estimates using:
      • material cost modeling
      • labor hour prediction
      • stochastic market drift
      • regional multipliers
      • multi‑factor weighted aggregation
    """

    def __init__(self):
        self.material_weights = {
            "lumber": 0.25,
            "concrete": 0.25,
            "steel": 0.25,
            "misc": 0.25
        }
        self.region_multipliers = {
            "default": 1.00,
            "urban": 1.15,
            "remote": 1.30
        }
        self._normalize()

    #---------------------------------------------------------------------------
    #  NORMALIZE MATERIAL WEIGHTS
    #---------------------------------------------------------------------------
    def _normalize(self):
        total = sum(self.material_weights.values())
        if total == 0:
            self.material_weights = {k: 0 for k in self.material_weights}
        else:
            self.material_weights = {k: v / total for k, v in self.material_weights.items()}

    #---------------------------------------------------------------------------
    #  STOCHASTIC MARKET DRIFT
    #---------------------------------------------------------------------------
    def _drift(self) -> float:
        return float(np.random.normal(1.0, 0.05))

    #---------------------------------------------------------------------------
    #  MATERIAL COST MODEL
    #---------------------------------------------------------------------------
    def material_cost(self, materials: Dict[str, float]) -> float:
        total = 0.0
        for m, qty in materials.items():
            w = self.material_weights.get(m, 0.10)
            base = qty * (50 + np.random.uniform(0, 20))
            total += base * w
        return total * self._drift()

    #---------------------------------------------------------------------------
    #  LABOR COST MODEL
    #---------------------------------------------------------------------------
    def labor_cost(self, hours: float, rate: float) -> float:
        return max(0.0, hours * rate * self._drift())

    #---------------------------------------------------------------------------
    #  TOTAL ESTIMATE
    #---------------------------------------------------------------------------
    def estimate(
        self,
        materials: Dict[str, float],
        labor_hours: float,
        labor_rate: float,
        region: str = "default"
    ) -> Dict[str, Any]:

        mat = self.material_cost(materials)
        lab = self.labor_cost(labor_hours, labor_rate)

        multiplier = self.region_multipliers.get(region, 1.00)
        total = (mat + lab) * multiplier

        return {
            "estimate_id": f"EST-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "inputs": {
                "materials": materials,
                "labor_hours": labor_hours,
                "labor_rate": labor_rate,
                "region": region
            },
            "components": {
                "material_cost": float(mat),
                "labor_cost": float(lab),
                "region_multiplier": multiplier
            },
            "total_estimate": float(total)
        }

    #---------------------------------------------------------------------------
    #  BATCH ESTIMATION
    #---------------------------------------------------------------------------
    def batch(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for d in dataset:
            r = self.estimate(
                d.get("materials", {}),
                d.get("labor_hours", 0.0),
                d.get("labor_rate", 0.0),
                d.get("region", "default")
            )
            results.append(r)
        return results

#===============================================================================
#  END OF FILE — construction_estimator.py
#===============================================================================
