# ============================================================
# TASK ROUTING ENGINE — Y‑PRIME EDITION
# ============================================================

import threading
import time

class TaskRoutingEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.routes = {}
        self.history = []
        self.limits = {"history": 200}

    # ============================================================
    # REGISTER ROUTE
    # ============================================================
    def register_route(self, task_type, module_id):
        with self.lock:
            self.routes[task_type] = module_id
            self._log()
            return {"registered": True}

    # ============================================================
    # RESOLVE ROUTE
    # ============================================================
    def resolve(self, task_type):
        return {"module": self.routes.get(task_type, None)}

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        self.history.append({"routes": len(self.routes), "ts": time.time()})
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {"routes": self.routes, "history": len(self.history)}
