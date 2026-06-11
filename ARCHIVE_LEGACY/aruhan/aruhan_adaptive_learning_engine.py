# ============================================================
# ARUHAN ADAPTIVE LEARNING ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

class AdaptiveLearningEngine:

    def __init__(self):
        self.weights = {
            "emo": 1.0,
            "mem": 1.0,
            "know": 1.0,
            "task": 1.0,
            "dlg": 1.0
        }
        self.learning_rate = 0.02
        self.decay = 0.001
        self.meta = {"drift":0.0,"bias":0.5,"coh":1.0}
        self.history = []
        self.limits = {"history":200}

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def process(self, emo, mem, know, task, dlg, orch, stab):
        self._update_weights(emo, mem, know, task, dlg, stab)
        self._apply_decay()
        self._meta_adjust(stab)
        self._log()
        return self._snapshot()

    # ============================================================
    # WEIGHT UPDATE
    # ============================================================
    def _update_weights(self, emo, mem, know, task, dlg, stab):
        drift = stab["state"]["drift"]
        coh = stab["state"]["coh"]
        bias = stab["state"]["bias"]

        adj = self.learning_rate * (1.0 - coh)
        self.weights["emo"] = max(0.1, min(2.0, self.weights["emo"] + adj * (abs(emo["m"]) + emo["st"])))
        self.weights["mem"] = max(0.1, min(2.0, self.weights["mem"] + adj * mem["meta"]["drift"]))
        self.weights["know"] = max(0.1, min(2.0, self.weights["know"] + adj * know["meta"]["bias"]))
        self.weights["task"] = max(0.1, min(2.0, self.weights["task"] + adj * task["meta"]["load"]))
        self.weights["dlg"] = max(0.1, min(2.0, self.weights["dlg"] + adj * (1.0 - coh)))

        if drift > 0.7:
            for k in self.weights:
                self.weights[k] = max(0.1, self.weights[k] * 0.95)

        if bias > 0.7 or bias < 0.3:
            self.weights["emo"] = (self.weights["emo"] + 1.0) / 2

    # ============================================================
    # DECAY
    # ============================================================
    def _apply_decay(self):
        for k in self.weights:
            self.weights[k] = max(0.1, self.weights[k] - self.decay)

    # ============================================================
    # META-ADJUSTMENT
    # ============================================================
    def _meta_adjust(self, stab):
        self.meta["drift"] = stab["state"]["drift"]
        self.meta["bias"] = stab["state"]["bias"]
        self.meta["coh"] = stab["state"]["coh"]

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        entry = {
            "weights": self.weights.copy(),
            "meta": self.meta.copy()
        }
        self.history.append(entry)
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def _snapshot(self):
        return {
            "weights": self.weights,
            "meta": self.meta,
            "history": len(self.history)
        }
