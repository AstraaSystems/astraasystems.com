import time

class ObjectivePermanenceEngine:
    """
    OBJECTIVE PERMANENCE ENGINE
    Maintains long-term emotional objectives and prevents emotional drift.
    Tracks:
    - emotional commitments
    - unresolved emotional states
    - long-term goals
    - emotional continuity across sessions

    Supports:
    - reinforcement of stable emotional identity
    - persistence of emotional objectives
    - decay of outdated objectives
    """

    def __init__(self):
        self.objectives = []
        self.decay_rate = 0.01  # slow decay over time
        self.last_update = time.time()

    def add_objective(self, emotion, intensity):
        entry = {
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": time.time(),
            "strength": self._initial_strength(intensity)
        }
        self.objectives.append(entry)

    def _initial_strength(self, intensity):
        return {
            "low": 1.0,
            "medium": 2.0,
            "high": 3.0
        }.get(intensity, 1.0)

    def update(self):
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Apply decay to all objectives
        for obj in self.objectives:
            obj["strength"] = max(0, obj["strength"] - (self.decay_rate * elapsed))

        # Remove fully decayed objectives
        self.objectives = [o for o in self.objectives if o["strength"] > 0]

    def strongest_objective(self):
        if not self.objectives:
            return None
        return max(self.objectives, key=lambda o: o["strength"])

    def process(self, emotion, intensity):
        # Add new objective
        if emotion != "neutral":
            self.add_objective(emotion, intensity)

        # Update decay
        self.update()

        # Return strongest objective
        return self.strongest_objective()
