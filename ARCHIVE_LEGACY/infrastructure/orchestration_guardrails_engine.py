# ============================================================
# ORCHESTRATION GUARDRAILS ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

import time
import threading

class OrchestrationGuardrailsEngine:

    def __init__(self):
        self.interactions = {}
        self.ttl_limits = {
            "task": 10,
            "loop": 3
        }
        self.timestamps = {}
        self.lock = threading.Lock()
        self.meta = {
            "loops_detected": 0,
            "kills": 0,
            "active_tasks": 0
        }
        self.history = []
        self.limits = {"history":200}

    # ============================================================
    # REGISTER TASK
    # ============================================================
    def register_task(self, task_id, module_a, module_b):
        with self.lock:
            key = f"{module_a}:{module_b}"
            if key not in self.interactions:
                self.interactions[key] = 0
            self.interactions[key] += 1
            self.timestamps[task_id] = time.time()
            self.meta["active_tasks"] += 1
            self._log()
            return {"registered": True}

    # ============================================================
    # CHECK LOOP
    # ============================================================
    def check_loop(self, module_a, module_b):
        key = f"{module_a}:{module_b}"
        if key not in self.interactions:
            return {"loop": False}

        if self.interactions[key] > self.ttl_limits["loop"]:
            self.meta["loops_detected"] += 1
            self._log()
            return {"loop": True, "pair": key}

        return {"loop": False}

    # ============================================================
    # CHECK TTL
    # ============================================================
    def check_ttl(self, task_id):
        if task_id not in self.timestamps:
            return {"expired": False}

        age = time.time() - self.timestamps[task_id]
        if age > self.ttl_limits["task"]:
            return {"expired": True, "age": age}

        return {"expired": False}

    # ============================================================
    # KILL TASK
    # ============================================================
    def kill_task(self, task_id):
        with self.lock:
            if task_id in self.timestamps:
                del self.timestamps[task_id]
            self.meta["kills"] += 1
            self.meta["active_tasks"] = max(0, self.meta["active_tasks"] - 1)
            self._log()
            return {"killed": True, "task": task_id}

    # ============================================================
    # RESET INTERACTIONS
    # ============================================================
    def reset_interactions(self):
        with self.lock:
            self.interactions = {}
            self._log()
            return {"reset": True}

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        entry = {
            "loops": self.meta["loops_detected"],
            "kills": self.meta["kills"],
            "active_tasks": self.meta["active_tasks"],
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
            "interactions": self.interactions,
            "meta": self.meta,
            "history": len(self.history)
        }
