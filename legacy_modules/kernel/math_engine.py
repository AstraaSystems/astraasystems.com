#!/usr/bin/env python3
# ============================================================
#  MATH ENGINE v17 — Arka Pillai Holdings Ltd
#  Handles: rounding, normalization, profit calculations
# ============================================================

class MathEngine:

    def round_currency(self, amount: float) -> float:
        return round(amount, 2)

    def normalize(self, value):
        if isinstance(value, str):
            try:
                return float(value.replace(",", ""))
            except:
                return 0.0
        return float(value)

    def compute_profit(self, revenue, cost):
        return self.round_currency(revenue - cost)
