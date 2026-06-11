# ============================================================
# JOB SCHEDULING ENGINE — Y‑PRIME EDITION
# ============================================================

import time
import threading

class JobSchedulingEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.queue = []
        self.meta = {"scheduled": 0, "executed": 0}
        self.history = []
        self.limits = {"history": 200}

    # ============================================================
    # SCHEDULE JOB
    # ============================================================
    def schedule(self, job):
        with self.lock:
            job["ts"] = time.time()
            self.queue.append(job)
            self.meta["scheduled"] += 1
            self._log()
            return {"scheduled": True}

    # ============================================================
    # NEXT JOB
    # ============================================================
    def next(self):
        with self.lock:
            if not self.queue:
                return {"job": None}
            job = self.queue.pop(0)
            self.meta["executed"] += 1
            self._log()
            return {"job": job}

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        self.history.append({"queue": len(self.queue), "ts": time.time()})
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {"queue": len(self.queue), "meta": self.meta}
