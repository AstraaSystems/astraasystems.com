# ============================================================
# KARPATHY OPTIMIZATION LOOP — Y‑PRIME EDITION
# ============================================================

import time
import threading

class KarpathyOptimizationLoop:

    def __init__(self):
        self.lock = threading.Lock()
        self.metrics = []
        self.limits = {"metrics": 200}

    # ============================================================
    # RECORD METRIC
    # ============================================================
    def record(self, value):
        with self.lock:
            self.metrics.append({"value": value, "ts": time.time()})
            if len(self.metrics) > self.limits["metrics"]:
                self.metrics.pop(0)
            return {"recorded": True}

    # ============================================================
    # COMPUTE TREND
    # ============================================================
    def trend(self):
        if len(self.metrics) < 2:
            return {"trend": "flat"}
        values = [m["value"] for m in self.metrics]
        if values[-1] > values[0]:
            return {"trend": "up"}
        if values[-1] < values[0]:
            return {"trend": "down"}
        return {"trend": "flat"}

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {"metrics": len(self.metrics)}
