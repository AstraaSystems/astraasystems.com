# ============================================================
# INFERENCE CONCURRENCY & VRAM LOCKING ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

import time
import threading

class InferenceConcurrencyEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.queue = []
        self.active = None
        self.vram_budget = {
            "total": 1.0,
            "used": 0.0
        }
        self.meta = {
            "queue_len": 0,
            "active": None,
            "last_release": 0.0
        }
        self.history = []
        self.limits = {"history":200}

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def request_access(self, module_id, vram_cost):
        ticket = {"id": module_id, "vram": vram_cost, "ts": time.time()}
        self.queue.append(ticket)
        self.meta["queue_len"] = len(self.queue)
        return self._attempt_lock()

    # ============================================================
    # ATTEMPT LOCK
    # ============================================================
    def _attempt_lock(self):
        if self.active is not None:
            return {"granted": False, "reason": "busy", "active": self.active}

        if not self.queue:
            return {"granted": False, "reason": "empty"}

        next_req = self.queue[0]

        if next_req["vram"] + self.vram_budget["used"] > self.vram_budget["total"]:
            return {"granted": False, "reason": "vram_limit"}

        acquired = self.lock.acquire(blocking=False)
        if not acquired:
            return {"granted": False, "reason": "lock_fail"}

        self.active = next_req["id"]
        self.vram_budget["used"] += next_req["vram"]
        self.queue.pop(0)
        self.meta["queue_len"] = len(self.queue)
        self._log()
        return {"granted": True, "module": self.active}

    # ============================================================
    # RELEASE LOCK
    # ============================================================
    def release(self, module_id, vram_cost):
        if self.active != module_id:
            return {"released": False, "reason": "not_owner"}

        self.vram_budget["used"] = max(0.0, self.vram_budget["used"] - vram_cost)
        self.active = None
        self.meta["last_release"] = time.time()
        try:
            self.lock.release()
        except:
            pass
        self._log()
        return {"released": True}

    # ============================================================
    # FORCE CLEAR (SAFETY)
    # ============================================================
    def force_clear(self):
        self.active = None
        self.queue = []
        self.vram_budget["used"] = 0.0
        try:
            self.lock.release()
        except:
            pass
        self.meta["queue_len"] = 0
        self._log()
        return {"cleared": True}

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        entry = {
            "active": self.active,
            "queue_len": self.meta["queue_len"],
            "vram_used": self.vram_budget["used"],
            "ts": time.time()
        }
        self.history.append(entry)
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {
            "active": self.active,
            "queue_len": self.meta["queue_len"],
            "vram": self.vram_budget,
            "history": len(self.history)
        }
