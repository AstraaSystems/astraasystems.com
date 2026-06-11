import time

class BehaviorPredictionEngine:
    """
    BEHAVIOR PREDICTION ENGINE
    Predicts:
    - emotional trajectory
    - likely next emotional state
    - user behavioral direction
    - relational movement (approach / withdraw)
    - escalation likelihood

    Inputs:
    - emotion
    - intensity
    - mood
    - baseline drift
    - internal state
    - emotional memory themes
    """

    def __init__(self):
        self.history = []
        self.max_history = 80

    def record(self, emotion, intensity, mood, baseline, internal_state, theme):
        entry = {
            "emotion": emotion,
            "intensity": intensity,
            "mood": mood,
            "baseline": baseline,
            "stability": internal_state.get("stability"),
            "clarity": internal_state.get("clarity"),
            "load": internal_state.get("cognitive_load"),
            "theme": theme["dominant_emotion"] if theme else None,
            "timestamp": time.time()
        }

        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def predict_emotional_shift(self, emotion, intensity, baseline):
        if emotion == "sadness" and intensity == "high":
            return "likely_deeper_negative"

        if emotion == "anger" and baseline < 0:
            return "likely_escalation"

        if emotion == "joy" and baseline > 0:
            return "likely_positive_stability"

        if baseline < -2:
            return "likely_negative_drift"

        if baseline > 2:
            return "likely_positive_drift"

        return "uncertain"

    def predict_relational_direction(self, emotion, intensity, stability):
        if emotion in ["anger", "fear"] and intensity == "high":
            return "withdraw"

        if stability < 0.3:
            return "unstable_withdraw"

        if emotion == "joy":
            return "approach"

        return "neutral"

    def predict(self, emotion, intensity, mood, baseline, internal_state, theme):
        self.record(emotion, intensity, mood, baseline, internal_state, theme)

        emotional_shift = self.predict_emotional_shift(emotion, intensity, baseline)
        relational_direction = self.predict_relational_direction(emotion, intensity, internal_state.get("stability"))

        return {
            "emotional_shift": emotional_shift,
            "relational_direction": relational_direction
        }
