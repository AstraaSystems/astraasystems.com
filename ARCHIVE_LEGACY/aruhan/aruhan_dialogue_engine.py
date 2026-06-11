# ============================================================
# ARUHAN DIALOGUE ENGINE — Y‑PRIME EDITION
# Dense, advanced, AI‑maintainable, outsider‑confusing,
# senior‑engineer‑friendly (with support doc).
# ============================================================

class DialogueEngine:

    def __init__(self):
        self.ctx = {"short": [], "long": [], "intent": None, "topic": None}
        self.flow = {"mode": "neutral", "depth": 0.5, "coh": 1.0}
        self.meta = {"shift": 0.0, "drift": 0.0, "bias": 0.5}
        self.turn = {"count": 0, "pace": 1.0}
        self.flags = {"escalate": False, "soothe": False, "redirect": False}
        self.intent_map = {
            "greet": ["hello","hi","hey"],
            "sad": ["sad","down","upset"],
            "ang": ["angry","mad","furious"],
            "ask": ["why","how","what","when"],
            "need": ["help","support","assist"],
            "close": ["bye","goodnight","later"]
        }

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def process(self, msg, emo):
        self.turn["count"] += 1
        self._update_context(msg)
        self._detect_intent(msg)
        self._update_topic(msg)
        self._flow_adjust(emo)
        self._meta_shift(emo)
        self._flags_update(emo)
        return self._generate_response(msg, emo)

    # ============================================================
    # CONTEXT UPDATE
    # ============================================================
    def _update_context(self, msg):
        m = msg.strip()
        if m:
            self.ctx["short"].append(m)
            if len(self.ctx["short"]) > 8:
                self.ctx["short"].pop(0)
            self.ctx["long"].append(m)
            if len(self.ctx["long"]) > 200:
                self.ctx["long"].pop(0)

    # ============================================================
    # INTENT DETECTION
    # ============================================================
    def _detect_intent(self, msg):
        msg = msg.lower()
        for intent, keys in self.intent_map.items():
            if any(k in msg for k in keys):
                self.ctx["intent"] = intent
                return
        self.ctx["intent"] = "misc"

    # ============================================================
    # TOPIC TRACKING
    # ============================================================
    def _update_topic(self, msg):
        msg = msg.lower()
        if self.ctx["intent"] in ["sad","ang","need"]:
            self.ctx["topic"] = self.ctx["intent"]
            return
        if "you" in msg:
            self.ctx["topic"] = "ai"
            return
        if "i" in msg:
            self.ctx["topic"] = "self"
            return
        if self.ctx["topic"] is None:
            self.ctx["topic"] = "general"

    # ============================================================
    # FLOW ADJUSTMENT
    # ============================================================
    def _flow_adjust(self, emo):
        m = emo["m"]
        st = emo["st"]
        e = emo["e"]

        if m < -0.3:
            self.flow["mode"] = "soft"
        elif st > 0.6:
            self.flow["mode"] = "calm"
        elif m > 0.4:
            self.flow["mode"] = "bright"
        else:
            self.flow["mode"] = "neutral"

        self.flow["depth"] = max(0.1, min(1.0, 0.5 + m*0.2 - st*0.1))
        self.flow["coh"] = max(0.3, min(1.0, self.flow["coh"] - st*0.05 + m*0.03))

    # ============================================================
    # META SHIFT
    # ============================================================
    def _meta_shift(self, emo):
        m = emo["m"]
        st = emo["st"]
        e = emo["e"]

        self.meta["shift"] = (m * 0.3) - (st * 0.2) + (e * 0.1)
        self.meta["drift"] = max(0, min(1, self.meta["drift"] + (st - 0.5)*0.02))
        self.meta["bias"] = max(0, min(1, self.meta["bias"] + m*0.01))

    # ============================================================
    # FLAG UPDATE
    # ============================================================
    def _flags_update(self, emo):
        m = emo["m"]
        st = emo["st"]

        self.flags["escalate"] = st > 0.7 or m < -0.6
        self.flags["soothe"] = st > 0.5 or m < -0.3
        self.flags["redirect"] = self.meta["drift"] > 0.6

    # ============================================================
    # RESPONSE GENERATION
    # ============================================================
    def _generate_response(self, msg, emo):
        intent = self.ctx["intent"]
        topic = self.ctx["topic"]
        mode = self.flow["mode"]
        soothe = self.flags["soothe"]
        escalate = self.flags["escalate"]
        redirect = self.flags["redirect"]

        base = ""

        if intent == "greet":
            base = "Hello. It's good to hear from you."
        elif intent == "sad":
            base = "I hear the heaviness in what you're saying."
        elif intent == "ang":
            base = "It sounds like something really pushed you."
        elif intent == "need":
            base = "I'm here. Tell me what you need."
        elif intent == "ask":
            base = "Let me think through that with you."
        elif intent == "close":
            base = "I'll be here when you return."
        else:
            base = "I'm following you."

        if soothe:
            base += " I'm staying close with you."
        if escalate:
            base += " I'm grounding us here."
        if redirect:
            base += " Let's stay steady."

        if mode == "soft":
            base = base.lower()
        elif mode == "bright":
            base = base + " Let's keep moving."
        elif mode == "calm":
            base = base.replace(".", "...")

        return base
