# ============================================================
# PIPELINE EXECUTION ENGINE — Y‑PRIME EDITION
# ============================================================

import threading
import time

class PipelineExecutionEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.pipelines = {}
        self.history = []
        self.limits = {"history": 200}

    # ============================================================
    # REGISTER PIPELINE
    # ============================================================
    def register(self, pipeline_id, steps):
        with self.lock:
            self.pipelines[pipeline_id] = {"steps": steps, "ts": time.time()}
            self._log()
            return {"registered": True}

    # ============================================================
    # EXECUTE PIPELINE
    # ============================================================
    def execute(self, pipeline_id):
        pipeline = self.pipelines.get(pipeline_id, None)
        if not pipeline:
            return {"executed": False, "reason": "not_found"}

        results = []
        for step in pipeline["steps"]:
            results.append({"step": step, "status": "ok"})

        self._log()
        return {"executed": True, "results": results}

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        self.history.append({"pipelines": len(self.pipelines), "ts": time.time()})
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {"pipelines": list(self.pipelines.keys()), "history": len(self.history)}
