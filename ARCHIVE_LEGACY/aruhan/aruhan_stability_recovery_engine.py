# ============================================================
# ARUHAN STABILITY & RECOVERY ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

class StabilityRecoveryEngine:

    def __init__(self):
        self.state = {"drift":0.0,"coh":1.0,"bias":0.5,"load":0.0}
        self.flags = {"unstable":False,"recover":False,"lockdown":False}
        self.thresholds = {"drift":0.65,"coh":0.45,"load":0.85}
        self.recovery = {"steps":0,"max_steps":5}
        self.history = []
        self.limits = {"history":200}

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def process(self, emo, mem, know, task, orch):
        self._update_state(emo, mem, know, task, orch)
        self._check_flags()
        self._apply_recovery()
        self._log()
        return self._snapshot()

    # ============================================================
    # STATE UPDATE
    # ============================================================
    def _update_state(self, emo, mem, know, task, orch):
        drift_vals = [
            mem["meta"]["drift"],
            know["meta"]["drift"],
            task["meta"]["drift"],
            orch["meta"]["drift"]
        ]
        bias_vals = [
            mem["meta"]["bias"],
            know["meta"]["bias"],
            task["meta"]["bias"],
            orch["meta"]["bias"]
        ]
        self.state["drift"] = sum(drift_vals) / 4
        self.state["bias"] = sum(bias_vals) / 4
        self.state["coh"] = max(0.0, min(1.0, 1.0 - abs(self.state["drift"] - 0.5)))
        self.state["load"] = task["queue"] / max(1, task["meta"]["load"] * task["queue"] + 1)

    # ============================================================
    # FLAG CHECKING
    # ============================================================
    def _check_flags(self):
        self.flags["unstable"] = (
            self.state["drift"] > self.thresholds["drift"] or
            self.state["coh"] < self.thresholds["coh"] or
            self.state["load"] > self.thresholds["load"]
        )
        self.flags["recover"] = self.flags["unstable"]
        self.flags["lockdown"] = self.state["drift"] > 0.85 or self.state["coh"] < 0.25

    # ============================================================
    # RECOVERY SYSTEM
    # ============================================================
    def _apply_recovery(self):
        if not self.flags["recover"]:
            self.recovery["steps"] = 0
            return

        if self.recovery["steps"] < self.recovery["max_steps"]:
            self.state["drift"] *= 0.92
            self.state["bias"] = (self.state["bias"] + 0.5) / 2
            self.state["coh"] = min(1.0, self.state["coh"] + 0.08)
            self.state["load"] *= 0.9
            self.recovery["steps"] += 1

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        entry = {
            "state": self.state.copy(),
            "flags": self.flags.copy(),
            "steps": self.recovery["steps"]
        }
        self.history.append(entry)
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def _snapshot(self):
        return {
            "state": self.state,
            "flags": self.flags,
            "steps": self.recovery["steps"],
            "history": len(self.history)
        }
