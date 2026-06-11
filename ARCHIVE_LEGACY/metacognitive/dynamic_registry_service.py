# ============================================================
# DYNAMIC REGISTRY SERVICE — Y‑PRIME EDITION
# ============================================================

import threading
import time

class DynamicRegistryService:

    def __init__(self):
        self.lock = threading.Lock()
        self.registry = {}
        self.meta = {"updates": 0}

    # ============================================================
    # REGISTER OR UPDATE ENTRY
    # ============================================================
    def register(self, key, value):
        with self.lock:
            self.registry[key] = {"value": value, "ts": time.time()}
            self.meta["updates"] += 1
            return {"registered": True}

    # ============================================================
    # GET ENTRY
    # ============================================================
    def get(self, key):
        return self.registry.get(key, None)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {"entries": len(self.registry), "updates": self.meta["updates"]}
