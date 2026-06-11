# ============================================================
# LOAD BALANCER ENGINE — Y‑PRIME EDITION
# ============================================================

import threading
import time

class LoadBalancerEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.loads = {}
        self.history = []
        self.limits = {"history": 200}

    # ============================================================
    # UPDATE LOAD
    # ============================================================
    def update_load(self, module_id, load_value):
        with self.lock:
            self.loads[module_id] = {"load": load_value, "ts": time.time()}
            self._log()
            return {"updated": True}

    # ============================================================
    # SELECT LOWEST LOAD
    # ============================================================
    def select(self):
        if not self.loads:
            return {"module": None}
        module = min(self.loads, key=lambda m: self.loads[m]["load"])
        return {"module": module}

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        self.history.append({"modules": len(self.loads), "ts": time.time()})
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {"loads": self.loads, "history": len(self.history)}
