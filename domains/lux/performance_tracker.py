# domains/lux/performance_tracker.py
class EconomicPerformanceTracker:
    def __init__(self):
        self.roi_ledger = {}

    def log_financial_outcome(self, decision_id: str, projected_value: float, actual_realized_value: float):
        """Maps machine decision accuracy directly to balance sheet performance."""
        net_variance = actual_realized_value - projected_value
        self.roi_ledger[decision_id] = {
            "pnl_impact": net_variance,
            "efficiency_ratio": actual_realized_value / projected_value if projected_value > 0 else 0
        }
