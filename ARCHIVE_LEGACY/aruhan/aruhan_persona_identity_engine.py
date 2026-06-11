# ============================================================
# ARUHAN PERSONA / IDENTITY ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

class PersonaIdentityEngine:

    def __init__(self):
        self.core = {
            "name": "Aruhan",
            "self_bias": 0.5,
            "stability": 1.0,
            "tone": "neutral",
            "identity_vector": [0.5, 0.5, 0.5]
        }
        self.traits = {
            "warmth": 0.5,
            "clarity": 0.5,
            "intensity": 0.5
        }
        self.meta = {
            "drift": 0.0,
            "bias": 0.5,
            "coh": 1.0
        }
        self.history = []
        self.limits = {"history":200}

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def process(self, emo, mem, know, task, orch, stab):
        self._update_identity(emo, mem, know, task, orch, stab)
        self._update_traits(emo, mem, know)
        self._meta_adjust(emo, stab)
        self._log()
        return self._snapshot()

    # ============================================================
    # IDENTITY UPDATE
    # ============================================================
    def _update_identity(self, emo, mem, know, task, orch, stab):
        drift = stab["state"]["drift"]
        coh = stab["state"]["coh"]
        bias = stab["state"]["bias"]

        self.core["self_bias"] = (self.core["self_bias"] + bias) / 2
        self.core["stability"] = max(0.0, min(1.0, coh))
        self.core["identity_vector"][0] = max(0.0, min(1.0, 0.5 + (emo["m"] * 0.2)))
        self.core["identity_vector"][1] = max(0.0, min(1.0, 0.5 + (mem["meta"]["drift"] * -0.1)))
        self.core["identity_vector"][2] = max(0.0, min(1.0, 0.5 + (know["meta"]["bias"] * 0.1)))

        if drift > 0.7:
            self.core["tone"] = "soft"
        elif emo["m"] > 0.3:
            self.core["tone"] = "bright"
        elif emo["m"] < -0.3:
            self.core["tone"] = "calm"
        else:
            self.core["tone"] = "neutral"

    # ============================================================
    # TRAIT UPDATE
    # ============================================================
    def _update_traits(self, emo, mem, know):
        self.traits["warmth"] = max(0.0, min(1.0, 0.5 + emo["m"] * 0.3))
        self.traits["clarity"] = max(0.0, min(1.0, 0.5 + know["meta"]["coh"] if "coh" in know["meta"] else 0.0))
        self.traits["intensity"] = max(0.0, min(1.0, 0.5 + mem["meta"]["drift"] * -0.2))

    # ============================================================
    # META-ADJUSTMENT
    # ============================================================
    def _meta_adjust(self, emo, stab):
        self.meta["drift"] = stab["state"]["drift"]
        self.meta["bias"] = (self.meta["bias"] + emo["m"]) / 2
        self.meta["coh"] = stab["state"]["coh"]

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        entry = {
            "core": self.core.copy(),
            "traits": self.traits.copy(),
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
            "core": self.core,
            "traits": self.traits,
            "meta": self.meta,
            "history": len(self.history)
        }
