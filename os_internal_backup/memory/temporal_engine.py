# os/memory/temporal_engine.py
import time

class TemporalEngine:
    def __init__(self):
        self.historical_performance_window = []  # Chronological ledger logs

    def calculate_temporal_trust_weight(self, current_accuracy: float, lookback_ticks: int = 3) -> float:
        """Computes a time-decayed trust coefficient based on short-horizon trends."""
        if not self.historical_performance_window:
            return 1.0
        
        recent_track = self.historical_performance_window[-lookback_ticks:]
        historical_avg = sum(run['accuracy'] for run in recent_track) / len(recent_track)
        
        # If short term accuracy collapses relative to historical performance, damp trust
        if historical_avg < 0.70:
            return 0.50  # Rapid protective trust mitigation
        return 1.0
