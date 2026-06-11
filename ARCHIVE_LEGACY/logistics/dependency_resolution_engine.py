# ============================================================
# DEPENDENCY RESOLUTION ENGINE — Y‑PRIME EDITION
# ============================================================

import threading
import time

class DependencyResolutionEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.dependencies = {}
        self.history = []
        self.limits = {"history": 200}

    # ============================================================
    # REGISTER DEPENDENCY
    # ============================================================
    def register(self, module_id, depends_on):
        with self.lock:
            self.dependencies[module_id] = depends_on
            self._log()
            return {"registered": True}

    # ============================================================
    # RESOLVE ORDER
    # ============================================================
    def resolve(self):
        resolved = []
        unresolved = list(self.dependencies.keys())

        while unresolved:
            progress = False
            for module in unresolved[:]:
                deps = self.dependencies[module]
                if all(d in resolved for d in deps):
                    resolved.append(module)
                    unresolved.remove(module)
                    progress = True
            if not progress:
                return {"resolved": False, "reason": "cycle_detected"}

        return {"resolved": True, "order": resolved}

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        self.history.append({"deps": len(self.dependencies), "ts": time.time()})
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {"dependencies": self.dependencies, "history": len(self.history)}
