import time

class MetaCognitionEngine:
    """
    META-COGNITION ENGINE
    Provides:
    - awareness of internal processes
    - evaluation of decision quality
    - monitoring of emotional reasoning
    - detection of cognitive bias patterns
    - meta-level insight generation
    """

    def __init__(self):
        self.history = []
        self.max_history = 40

    def record(self, cognition, delegation, reflection, internal_state):
        entry = {
            "cognition": cognition,
            "delegation": delegation,
            "reflection": reflection,
            "stability": internal_state.get("stability"),
            "clarity": internal_state.get("clarity"),
            "load": internal_state.get("cognitive_load"),
            "timestamp": time.time()
        }

        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def analyze(self):
        if len(self.history) < 5:
            return None

        bias_signals = []
        overload_signals = []
        clarity_signals = []

        for h in self.history:
            if h["delegation"] == "handle_internal" and h["load"] > 3:
                overload_signals.append("overconfident_under_load")

            if h["clarity"] < 0.3 and h["delegation"] == "handle_internal":
                clarity_signals.append("low_clarity_decision")

            if h["reflection"] and "sustained_negative_mood" in h["reflection"]:
                bias_signals.append("negative_bias")

        insights = []

        if len(overload_signals) >= 2:
            insights.append("meta_overload_detected")

        if len(clarity_signals) >= 2:
            insights.append("meta_clarity_issue")

        if len(bias_signals) >= 2:
            insights.append("meta_negative_bias")

        return insights if insights else None

    def reflect(self, cognition, delegation, reflection, internal_state):
        self.record(cognition, delegation, reflection, internal_state)
        return self.analyze()
