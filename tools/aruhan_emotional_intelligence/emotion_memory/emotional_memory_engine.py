import time

class EmotionalMemoryEngine:
    """
    LONG-TERM EMOTIONAL MEMORY ENGINE
    Stores emotional experiences with:
    - weighted emotional significance
    - decay over time
    - reinforcement when similar emotions recur
    - emotional tagging
    - retrieval of dominant emotional themes

    Memory entries:
    {
        "emotion": str,
        "intensity": str,
        "tone": str,
        "timestamp": float,
        "weight": float
    }
    """

    def __init__(self):
        self.memory = []
        self.max_memory = 300
        self.decay_rate = 0.002  # slow decay per second

    def _initial_weight(self, intensity):
        return {
            "low": 1.0,
            "medium": 2.0,
            "high": 3.5
        }.get(intensity, 1.0)

    def store(self, emotion, intensity, tone):
        entry = {
            "emotion": emotion,
            "intensity": intensity,
            "tone": tone,
            "timestamp": time.time(),
            "weight": self._initial_weight(intensity)
        }

        self.memory.append(entry)

        # Enforce memory cap
        if len(self.memory) > self.max_memory:
            self.memory.pop(0)

    def decay(self):
        now = time.time()
        for entry in self.memory:
            elapsed = now - entry["timestamp"]
            entry["weight"] = max(0, entry["weight"] - (elapsed * self.decay_rate))
            entry["timestamp"] = now

        # Remove fully decayed memories
        self.memory = [m for m in self.memory if m["weight"] > 0]

    def reinforce(self, emotion):
        for entry in self.memory:
            if entry["emotion"] == emotion:
                entry["weight"] += 0.5

    def dominant_themes(self):
        if not self.memory:
            return None

        themes = {}
        for entry in self.memory:
            themes.setdefault(entry["emotion"], 0)
            themes[entry["emotion"]] += entry["weight"]

        dominant = max(themes, key=themes.get)
        return {
            "dominant_emotion": dominant,
            "weight": themes[dominant]
        }

    def process(self, emotion, intensity, tone):
        if emotion != "neutral":
            self.store(emotion, intensity, tone)
            self.reinforce(emotion)

        self.decay()

        return self.dominant_themes()
