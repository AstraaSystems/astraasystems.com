import time

class SelfReflectionEngine:
    """
    SELF-REFLECTION ENGINE
    Allows Aruhan to:
    - evaluate internal emotional patterns
    - reflect on recent emotional states
    - generate self-awareness metrics
    - detect contradictions between mood, tone, and emotion
    - produce internal insights
    """

    def __init__(self):
        self.history = []
        self.max_history = 50

    def record(self, emotion, intensity, mood, baseline, internal_state):
        entry = {
            "emotion": emotion,
            "intensity": intensity,
            "mood": mood,
            "baseline": baseline,
            "stability": internal_state.get("stability"),
            "clarity": internal_state.get("clarity"),
            "load": internal_state.get("cognitive_load"),
            "timestamp": time.time()
        }

        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def analyze_patterns(self):
        if len(self.history) < 5:
            return None

        negative_count = sum(1 for h in self.history if "negative" in h["mood"])
        high_load_count = sum(1 for h in self.history if h["load"] > 3)
        low_clarity_count = sum(1 for h in self.history if h["clarity"] < 0.4)

        insights = []

        if negative_count >= 3:
            insights.append("sustained_negative_mood")

        if high_load_count >= 2:
            insights.append("cognitive_overload")

        if low_clarity_count >= 2:
            insights.append("clarity_instability")

        if not insights:
            return None

        return insights

    def reflect(self, emotion, intensity, mood, baseline, internal_state):
        self.record(emotion, intensity, mood, baseline, internal_state)
        return self.analyze_patterns()
