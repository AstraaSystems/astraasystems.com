# ============================================================
# ARUHAN SECURITY AI MODULE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

class SecurityAIModule:

    def __init__(self):
        self.integrity = {"emo":True,"mem":True,"know":True,"task":True,"dlg":True,"orch":True}
        self.threat = {"level":0.0,"type":"none"}
        self.flags = {"contain":False,"lockdown":False,"violation":False}
        self.thresholds = {"drift":0.65,"coh":0.45,"load":0.85,"critical_drift":0.90,"critical_coh":0.20}
        self.history = []
        self.limits = {"history":200}

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def process(self, emo, mem, know, task, dlg, orch, stab):
        self._integrity_check(emo, mem, know, task, dlg, orch)
        self._threat_eval(emo, mem, know, task, orch, stab)
        self._apply_containment()
        self._apply_lockdown()
        self._log()
        return self._snapshot()

    # ============================================================
    # INTEGRITY CHECK
    # ============================================================
    def _integrity_check(self, emo, mem, know, task, dlg, orch):
        self.integrity["emo"] = isinstance(emo, dict)
        self.integrity["mem"] = isinstance(mem, dict)
        self.integrity["know"] = isinstance(know, dict)
        self.integrity["task"] = isinstance(task, dict)
        self.integrity["dlg"] = isinstance(dlg, str)
        self.integrity["orch"] = isinstance(orch, dict)
        self.flags["violation"] = not all(self.integrity.values())

    # ============================================================
    # THREAT EVALUATION
    # ============================================================
    def _threat_eval(self, emo, mem, know, task, orch, stab):
        drift = stab["state"]["drift"]
        coh = stab["state"]["coh"]
        load = stab["state"]["load"]

        score = 0.0
        if drift > self.thresholds["drift"]:
            score += 0.4
        if coh < self.thresholds["coh"]:
            score += 0.3
        if load > self.thresholds["load"]:
            score += 0.3
        if self.flags["violation"]:
            score += 0.5

        self.threat["level"] = min(1.0, score)

        if drift > self.thresholds["critical_drift"]:
            self.threat["type"] = "critical_drift"
        elif coh < self.thresholds["critical_coh"]:
            self.threat["type"] = "critical_coherence"
        elif load > self.thresholds["load"]:
            self.threat["type"] = "overload"
        elif self.flags["violation"]:
            self.threat["type"] = "integrity_violation"
        else:
            self.threat["type"] = "none"

    # ============================================================
    # CONTAINMENT
    # ============================================================
    def _apply_containment(self):
        self.flags["contain"] = self.threat["level"] >= 0.5 and not self.flags["lockdown"]

    # ============================================================
    # LOCKDOWN
    # ============================================================
    def _apply_lockdown(self):
        self.flags["lockdown"] = (
            self.threat["type"] in ["critical_drift","critical_coherence"] or
            self.flags["violation"]
        )

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        entry = {
            "integrity": self.integrity.copy(),
            "threat": self.threat.copy(),
            "flags": self.flags.copy()
        }
        self.history.append(entry)
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def _snapshot(self):
        return {
            "integrity": self.integrity,
            "threat": self.threat,
            "flags": self.flags,
            "history": len(self.history)
        }
