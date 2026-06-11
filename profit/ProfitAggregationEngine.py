#!/usr/bin/env python3
# ============================================================
#  PROFIT AGGREGATION ENGINE v17 — Arka Pillai Holdings Ltd
#  Handles:
#   - revenue collection from all engines
#   - normalization
#   - ledger reconciliation
#   - divergence detection
#   - profit snapshot generation
#   - Lux allocation (20%)
# ============================================================

import json
import os
from datetime import datetime

class ProfitAggregationEngine:

    def __init__(self, kernel, supervisor):
        self.kernel = kernel
        self.supervisor = supervisor

        self.snapshot_path = "/home/keshanth/ARKA/ardhanarishvara/profit/profit_snapshot.json"
        os.makedirs("/home/keshanth/ARKA/ardhanarishvara/profit/", exist_ok=True)

        if not os.path.exists(self.snapshot_path):
            with open(self.snapshot_path, "w") as f:
                json.dump({"history": []}, f, indent=4)

    # ============================================================
    #  MAIN ENTRYPOINT
    # ============================================================

    def aggregate(self):
        ledger_data = self.kernel.ledger.load()

        total_revenue = 0.0
        total_cost = 0.0

        engine_breakdown = {}

        # --------------------------------------------------------
        # 1. Collect revenue from ledger
        # --------------------------------------------------------
        for entry in ledger_data:
            result = entry.get("result", {})

            revenue = result.get("revenue_generated") or result.get("cycle_revenue") or 0.0
            cost = result.get("cost") or 0.0

            revenue = self.kernel.math.normalize(revenue)
            cost = self.kernel.math.normalize(cost)

            total_revenue += revenue
            total_cost += cost

            engine = entry.get("engine", "Unknown")
            engine_breakdown.setdefault(engine, {"revenue": 0.0, "cost": 0.0})
            engine_breakdown[engine]["revenue"] += revenue
            engine_breakdown[engine]["cost"] += cost

        # --------------------------------------------------------
        # 2. Compute profit
        # --------------------------------------------------------
        total_profit = self.kernel.math.compute_profit(total_revenue, total_cost)

        # --------------------------------------------------------
        # 3. Lux allocation (20%)
        # --------------------------------------------------------
        allocation = self.kernel.lux.allocate(total_profit)

        # --------------------------------------------------------
        # 4. Build snapshot
        # --------------------------------------------------------
        snapshot = {
            "timestamp": str(datetime.now()),
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": total_profit,
            "lux_allocation": allocation["lux_allocation"],
            "retained_profit": allocation["retained_profit"],
            "engine_breakdown": engine_breakdown
        }

        # --------------------------------------------------------
        # 5. Save snapshot
        # --------------------------------------------------------
        with open(self.snapshot_path, "r") as f:
            data = json.load(f)

        data["history"].append(snapshot)

        with open(self.snapshot_path, "w") as f:
            json.dump(data, f, indent=4)

        return snapshot

    # ============================================================
    #  DIVERGENCE DETECTION
    # ============================================================

    def detect_divergence(self):
        ledger_data = self.kernel.ledger.load()
        issues = []

        for entry in ledger_data:
            result = entry.get("result", {})
            revenue = result.get("revenue_generated") or result.get("cycle_revenue")

            if revenue is None:
                issues.append({
                    "timestamp": entry["timestamp"],
                    "engine": entry["engine"],
                    "issue": "Missing revenue field"
                })

        return issues
