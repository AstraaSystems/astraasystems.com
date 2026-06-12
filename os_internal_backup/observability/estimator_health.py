import time
from typing import Dict, Any

class EstimatorHealthMonitor:
    def __init__(self):
        self.metrics_registry = {}

    def record_execution_telemetry(self, node_id: str, latency_ms: float, variance: float) -> Dict[str, Any]:
        """Tracks live node structural health without disrupting execution paths."""
        self.metrics_registry[node_id] = {
            "timestamp": time.time(),
            "latency_ms": latency_ms,
            "variance_drift": variance,
            "status": "HEALTHY" if variance < 0.8 else "DRIFT_WARNING"
        }
        return self.metrics_registry[node_id]
