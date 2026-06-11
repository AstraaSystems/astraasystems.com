# ============================================================
# ARUHAN MEMORY ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

class MemoryEngine:

    def __init__(self):
        self.stm = []          # short-term memory buffer
        self.ltm = []          # long-term memory buffer
        self.ep = []           # episodic memory
        self.sem = {}          # semantic memory
        self.weights = {"stm":1.0,"ltm":1.0,"ep":1.0,"sem":1.0}
        self.decay = {"stm":0.12,"ltm":0.005,"ep":0.01,"sem":0.0}
        self.limits = {"stm":12,"ltm":500,"ep":300}
        self.meta = {"drift":0.0,"bias":0.5,"coh":1.0}

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def process(self, msg, emo):
        self._stm_add(msg)
        self._ltm_add(msg, emo)
        self._ep_add(msg, emo)
        self._sem_update(msg)
        self._apply_decay()
        self._meta_adjust(emo)
        return self._snapshot()

    # ============================================================
    # SHORT-TERM MEMORY
    # ============================================================
    def _stm_add(self, msg):
        if msg:
            self.stm.append(msg)
            if len(self.stm) > self.limits["stm"]:
                self.stm.pop(0)

    # ============================================================
    # LONG-TERM MEMORY
    # ============================================================
    def _ltm_add(self, msg, emo):
        if not msg:
            return
        m = emo["m"]
        st = emo["st"]
        e = emo["e"]
        score = (abs(m) * 0.4) + (st * 0.3) + (e * 0.1)
        if score > 0.25:
            self.ltm.append({"msg":msg,"m":m,"st":st,"e":e})
            if len(self.ltm) > self.limits["ltm"]:
                self.ltm.pop(0)

    # ============================================================
    # EPISODIC MEMORY
    # ============================================================
    def _ep_add(self, msg, emo):
        if not msg:
            return
        m = emo["m"]
        st = emo["st"]
        e = emo["e"]
        tag = "neg" if m < -0.3 else "pos" if m > 0.3 else "neu"
        ep = {"msg":msg,"tag":tag,"m":m,"st":st,"e":e}
        self.ep.append(ep)
        if len(self.ep) > self.limits["ep"]:
            self.ep.pop(0)

    # ============================================================
    # SEMANTIC MEMORY
    # ============================================================
    def _sem_update(self, msg):
        if not msg:
            return
        words = msg.lower().split()
        for w in words:
            if w not in self.sem:
                self.sem[w] = 1
            else:
                self.sem[w] += 1

    # ============================================================
    # DECAY SYSTEM
    # ============================================================
    def _apply_decay(self):
        d_stm = self.decay["stm"]
        d_ltm = self.decay["ltm"]
        d_ep = self.decay["ep"]

        if len(self.stm) > 0:
            if d_stm > 0:
                if len(self.stm) > 2:
                    self.stm = self.stm[int(d_stm*len(self.stm)):]
        
        if len(self.ltm) > 0:
            if d_ltm > 0:
                cut = int(d_ltm * len(self.ltm))
                if cut > 0:
                    self.ltm = self.ltm[cut:]

        if len(self.ep) > 0:
            if d_ep > 0:
                cut = int(d_ep * len(self.ep))
                if cut > 0:
                    self.ep = self.ep[cut:]

    # ============================================================
    # META-ADJUSTMENT
    # ============================================================
    def _meta_adjust(self, emo):
        m = emo["m"]
        st = emo["st"]
        e = emo["e"]
        self.meta["drift"] = max(0, min(1, self.meta["drift"] + (st - 0.5)*0.01))
        self.meta["bias"] = max(0, min(1, self.meta["bias"] + m*0.005))
        self.meta["coh"] = max(0.3, min(1.0, self.meta["coh"] - st*0.02 + e*0.01))

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def _snapshot(self):
        return {
            "stm": self.stm[-5:],
            "ltm_count": len(self.ltm),
            "ep_count": len(self.ep),
            "sem_keys": len(self.sem),
            "meta": self.meta
        }
