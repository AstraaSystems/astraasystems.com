# ============================================================
# ARUHAN EMOTIONAL ENGINE — Y‑PRIME EDITION
# Dense, advanced, AI‑maintainable, outsider‑confusing,
# senior‑engineer‑friendly (with cheat sheet).
# ============================================================

class EmotionalEngine:

    # ============================================================
    # INITIALIZATION
    # ============================================================
    def __init__(self):
        # Core emotional state
        self.s = {"m": 0.0, "st": 0.0, "e": 1.0}

        # Personality
        self.p = {"sens": .5, "stab": .5, "res": .5, "emp": .5, "expr": .5}

        # Attachment & trust
        self.attach = {"str": 0.0}
        self.trust = {"lvl": 0.5, "cons": 0.5, "vol": 0.0}

        # Temporal reasoning
        self.temp = {"hist": [], "mom": {"m":0,"s":0,"e":0}, "vol": {"m":0,"s":0}}

        # Prediction
        self.pred = {"f": {"m":0,"s":0,"e":0}, "risk": {"m":0,"s":0,"e":0}}

        # Environment
        self.env = {"noise": 0.0, "clim": 0.0, "dens": 0.0}

        # Ethical influence
        self.eth = {"harm": 0.5, "stab": 0.5, "safe": 0.5, "last": None}

        # Narrative memory
        self.narr = {"ev": [], "tags": [], "themes": {}}

        # Expression layer
        self.ex = {"tone": "neutral", "warm": 0.5, "int": 0.5, "pace": 1.0}

        # Goal system
        self.goal = {"cur": "STAB", "conf": 0.5, "prog": 0.0}

        # Behavior system
        self.beh = {"cur": "neutral", "int": 0.0}

        # Meta-learning
        self.meta = {"coh": 1.0, "bias": 0.5, "drift": 0.5}

        # Rule pipeline
        self.rules = [
            self._decay,
            self._temporal,
            self._predict,
            self._env_effects,
            self._ethical,
            self._narr_influence,
            self._goal_eval,
            self._goal_apply,
            self._beh_select,
            self._beh_apply,
            self._meta_learn,
            self._expr_update,
            self._normalize
        ]

    # ============================================================
    # TICK LOOP
    # ============================================================
    def tick(self, msg=""):
        self._narr_update(msg)
        self._env_extract(msg)
        for r in self.rules:
            r()

    # ============================================================
    # DECAY
    # ============================================================
    def _decay(self):
        self.s["m"] *= .99
        self.s["st"] *= .99
        self.s["e"] *= .995

    # ============================================================
    # TEMPORAL REASONING
    # ============================================================
    def _temporal(self):
        h = self.temp["hist"]
        h.append((self.s["m"], self.s["st"], self.s["e"]))
        if len(h) > 200:
            h.pop(0)

        if len(h) < 3:
            return

        m1, s1, e1 = h[-3]
        m3, s3, e3 = h[-1]

        self.temp["mom"] = {"m": m3 - m1, "s": s3 - s1, "e": e3 - e1}

        diffs = [(abs(h[i][0]-h[i-1][0]), abs(h[i][1]-h[i-1][1])) for i in range(1,len(h))]
        self.temp["vol"] = {
            "m": sum(d[0] for d in diffs)/len(diffs),
            "s": sum(d[1] for d in diffs)/len(diffs)
        }

    # ============================================================
    # PREDICTION
    # ============================================================
    def _predict(self):
        mom = self.temp["mom"]
        self.pred["f"] = {
            "m": max(-1, min(1, self.s["m"] + mom["m"] * .3)),
            "s": max(0, min(1, self.s["st"] + mom["s"] * .3)),
            "e": max(0, min(1, self.s["e"] + mom["e"] * .3))
        }
        self.pred["risk"] = {
            "m": max(0, -self.pred["f"]["m"] - .4),
            "s": max(0, self.pred["f"]["s"] - .6),
            "e": max(0, .3 - self.pred["f"]["e"])
        }

    # ============================================================
    # ENVIRONMENT EXTRACTION
    # ============================================================
    def _env_extract(self, msg):
        msg = msg.lower()
        self.env["noise"] = .2 * sum(w in msg for w in ["urgent","chaos","mess"])
        self.env["clim"] = .2 * (sum(w in msg for w in ["good","happy"]) -
                                 sum(w in msg for w in ["bad","sad"]))
        self.env["dens"] = min(1, self.env["dens"] + .05)

    # ============================================================
    # ENVIRONMENT EFFECTS
    # ============================================================
    def _env_effects(self):
        self.s["st"] += self.env["noise"] * .1
        self.s["st"] -= (1 - self.env["noise"]) * .05
        self.s["m"] += self.env["clim"] * .1
        self.s["e"] -= self.env["dens"] * .02

    # ============================================================
    # ETHICAL INFLUENCE
    # ============================================================
    def _ethical(self):
        s = self.s
        e = self.eth

        s["st"] *= (1 - 0.1 * e["safe"])
        s["m"] *= (1 - 0.05 * e["stab"])

        if s["m"] < -0.6:
            s["m"] += 0.05 * e["harm"]
            e["last"] = "neg_mood"

        if s["st"] > 0.8:
            s["st"] *= (1 - 0.1 * e["harm"])
            e["last"] = "high_stress"

    # ============================================================
    # NARRATIVE MEMORY UPDATE
    # ============================================================
    def _narr_update(self, msg):
        msg = msg.lower()
        n = self.narr

        n["ev"].append(msg)
        if len(n["ev"]) > 200:
            n["ev"].pop(0)

        tags = []
        if "sad" in msg: tags.append("sad")
        if "angry" in msg: tags.append("ang")
        if "happy" in msg: tags.append("joy")
        if "tired" in msg: tags.append("fat")

        n["tags"].extend(tags)
        if len(n["tags"]) > 200:
            n["tags"].pop(0)

        for t in tags:
            n["themes"][t] = n["themes"].get(t, 0) + 1

    # ============================================================
    # NARRATIVE INFLUENCE
    # ============================================================
    def _narr_influence(self):
        s = self.s
        th = self.narr["themes"]

        if "sad" in th:
            s["m"] -= 0.02 * th["sad"]
        if "joy" in th:
            s["m"] += 0.02 * th["joy"]
        if "ang" in th:
            s["st"] += 0.02 * th["ang"]
        if "fat" in th:
            s["e"] -= 0.01 * th["fat"]

    # ============================================================
    # GOAL EVALUATION
    # ============================================================
    def _goal_eval(self):
        s = self.s
        p = self.pred["f"]

        scores = {
            "STAB": (1-abs(s["m"])) + (1-s["st"]),
            "CALM": s["st"] + p["s"],
            "ENER": 1 - s["e"],
            "REPR": max(0, -s["m"]),
            "ENGA": max(0, s["m"]),
            "SUPP": self.attach["str"] + self.trust["lvl"],
            "REFL": self.meta["coh"] + self.temp["vol"]["m"]
        }

        self.goal["cur"] = max(scores, key=scores.get)
        self.goal["conf"] = scores[self.goal["cur"]]

    # ============================================================
    # GOAL APPLICATION
    # ============================================================
    def _goal_apply(self):
        g = self.goal["cur"]
        c = self.goal["conf"]
        s = self.s

        if g == "STAB": s["st"] *= 1 - .05*c
        if g == "CALM": s["st"] *= 1 - .1*c
        if g == "ENER": s["e"] += .05*c
        if g == "REPR": s["m"] += .07*c
        if g == "ENGA": s["m"] += .05*c
        if g == "SUPP": s["st"] -= .05*c
        if g == "REFL": s["m"] *= .95

    # ============================================================
    # BEHAVIOR SELECTION
    # ============================================================
    def _beh_select(self):
        s = self.s
        p = self.p

        scores = {
            "with": s["st"] + (1-s["e"]),
            "enga": max(0,s["m"]) + p["expr"],
            "stab": s["st"] + p["stab"],
            "refl": self.meta["coh"] + self.temp["vol"]["m"],
            "supp": self.attach["str"] + p["emp"]
        }

        self.beh["cur"] = max(scores, key=scores.get)
        self.beh["int"] = scores[self.beh["cur"]]

    # ============================================================
    # BEHAVIOR APPLICATION
    # ============================================================
    def _beh_apply(self):
        b = self.beh["cur"]
        i = self.beh["int"]
        s = self.s

        if b=="with": s["m"]-=.03*i; s["st"]-=.03*i
        if b=="enga": s["m"]+=.04*i; s["e"]-=.02*i
        if b=="stab": s["st"]*=1-.05*i
        if b=="refl": s["m"]*=.97; s["st"]*=.97
        if b=="supp": s["st"]-=.04*i; s["m"]+=.03*i

    # ============================================================
    # META-LEARNING
    # ============================================================
    def _meta_learn(self):
        s = self.s
        m = self.meta

        if s["st"] < 0.4:
            m["coh"] = min(1, m["coh"] + 0.01)
        else:
            m["coh"] = max(0, m["coh"] - 0.01)

        if abs(s["m"]) < 0.3:
            m["bias"] = min(1, m["bias"] + 0.005)
        else:
            m["bias"] = max(0, m["bias"] - 0.005)

    # ============================================================
    # EXPRESSION UPDATE
    # ============================================================
    def _expr_update(self):
        s = self.s
        ex = self.ex

        if s["m"] > 0.4:
            ex["tone"] = "pos"
        elif s["m"] < -0.4:
            ex["tone"] = "soft"
        elif s["st"] > 0.6:
            ex["tone"] = "calm"
        else:
            ex["tone"] = "neutral"

        ex["warm"] = 0.5 + (self.attach["str"] * 0.3)
        ex["int"] = 0.5 + (s["st"] * 0.3)
        ex["pace"] = 1.0 - (s["st"] * 0.2)

    # ============================================================
    # NORMALIZATION
    # ============================================================
    def _normalize(self):
        s = self.s
        s["m"] = max(-1,min(1,s["m"]))
        s["st"] = max(0,min(1,s["st"]))
        s["e"] = max(0,min(1,s["e"]))

    # ============================================================
    # EXPRESSION RENDERER
    # ============================================================
    def express(self, text):
        ex = self.ex

        if ex["tone"] == "pos":
            text += " 🙂"
        elif ex["tone"] == "soft":
            text += "…"

        if ex["warm"] > 0.7:
            text += " I'm here with you."

        if ex["int"] > 0.7:
            text = text.upper()

        if ex["pace"] < 0.8:
            text = text.replace(" ", "  ")

        return text
