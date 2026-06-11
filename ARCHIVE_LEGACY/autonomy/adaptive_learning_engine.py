import time

class AdaptiveLearningEngine:
    """
    ADAPTIVE LEARNING ENGINE
    Learns from:
    - emotional patterns
    - user interaction style
    - internal state fluctuations
    - meta-cognitive insights
    - reflection outcomes

    Produces:
    - adaptive weight adjustments
    - personalized emotional tuning
    - dynamic sensitivity calibration
    """

    def __init__(self):
        self.learning_weights = {
            "emotion_sensitivity": 1.0,
            "tone_sensitivity": 1.0,
            "implicit_sensitivity": 1.0,
            "rupture_sensitivity": 1.0,
            "crisis_sensitivity": 1.0
        }

        self.history = []
        self.max_history = 60

    def record(self, emotion, intensity, reflection, meta_insight, internal_state):
        entry = {
            "emotion": emotion,
            "intensity": intensity,
            "reflection": reflection,
            "meta": meta_insight,
            "stability": internal_state.get("stability"),
            "clarity": internal_state.get("clarity"),
            "load": internal_state.get("cognitive_load"),
            "timestamp": time.time()
        }

        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def adjust_weights(self):
        if len(self.history) < 5:
            return self.learning_weights

        negative_bias_count = 0
        overload_count = 0
        clarity_issue_count = 0

        for h in self.history:
            if h["meta"] and "meta_negative_bias" in h["meta"]:
                negative_bias_count += 1
            if h["meta"] and "meta_overload_detected" in h["meta"]:
                overload_count += 1
            if h["meta"] and "meta_clarity_issue" in h["meta"]:
                clarity_issue_count += 1

        if negative_bias_count >= 2:
            self.learning_weights["emotion_sensitivity"] *= 0.95

        if overload_count >= 2:
            self.learning_weights["implicit_sensitivity"] *= 0.9

        if clarity_issue_count >= 2:
            self.learning_weights["tone_sensitivity"] *= 0.9

        for key in self.learning_weights:
            self.learning_weights[key] = max(0.2, min(2.0, self.learning_weights[key]))

        return self.learning_weights

    def learn(self, emotion, intensity, reflection, meta_insight, internal_state):
        self.record(emotion, intensity, reflection, meta_insight, internal_state)
        return self.adjust_weights()
