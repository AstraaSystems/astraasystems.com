# ============================================================
# ARUHAN SYSTEM ORCHESTRATOR — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

class SystemOrchestrator:

    def __init__(self, emo, dlg, mem, know, task):
        self.emo = emo
        self.dlg = dlg
        self.mem = mem
        self.know = know
        self.task = task
        self.meta = {"load":0.0,"drift":0.0,"bias":0.5,"sync":1.0}
        self.pipeline = ["emo","mem","know","task","dlg"]
        self.history = []
        self.limits = {"history":300}

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def process(self, msg):
        emo_out = self.emo.process(msg)
        mem_out = self.mem.process(msg, emo_out)
        know_out = self.know.process(msg, mem_out, emo_out)
        task_out = self.task.process(msg, emo_out, mem_out, know_out)
        dlg_out = self.dlg.process(msg, emo_out)
        self._sync(emo_out, mem_out, know_out, task_out)
        self._log(msg, dlg_out)
        return dlg_out

    # ============================================================
    # SYNCHRONIZATION
    # ============================================================
    def _sync(self, emo, mem, know, task):
        load = task["queue"] / max(1, self.task.limits["queue"])
        drift = (emo["st"] + mem["meta"]["drift"] + know["meta"]["drift"] + task["meta"]["drift"]) / 4
        bias = (emo["m"] + mem["meta"]["bias"] + know["meta"]["bias"] + task["meta"]["bias"]) / 4
        self.meta["load"] = min(1.0, load)
        self.meta["drift"] = max(0, min(1, drift))
        self.meta["bias"] = max(0, min(1, bias))
        self.meta["sync"] = max(0.3, 1.0 - abs(self.meta["drift"] - 0.5))

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self, msg, out):
        entry = {"in":msg,"out":out,"meta":self.meta.copy()}
        self.history.append(entry)
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {
            "meta": self.meta,
            "history": len(self.history),
            "pipeline": self.pipeline
        }
