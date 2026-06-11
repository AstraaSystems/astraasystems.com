import random
import time

class InternalStateSimulator:
    """
    INTERNAL STATE SIMULATOR
    Simulates Aruhan's internal emotional landscape:
    - stability
    - clarity
    - cognitive load
    - emotional turbulence
    - internal drift over time

    This creates a realistic internal emotional world.
    """

    def __init__(self):
        self.stability = 1.0      # 0.0 = unstable, 1.0 = stable
        self.clarity = 1.0        # 0.0 = foggy, 1.0 = clear
        self.cognitive_load = 0.0 # 0.0 = free, 5.0 = overloaded
        self.last_update = time.time()

    def update(self, mood, residue, crisis_level):
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Cognitive load increases with emotional residue
        self.cognitive_load = min(5.0, residue * 0.8)

        # Crisis reduces stability
        if crisis_level == "critical":
            self.stability = max(0.1, self.stability - 0.3)
        elif crisis_level == "high":
            self.stability = max(0.2, self.stability - 0.15)
        else:
            # Natural recovery
            self.stability = min(1.0, self.stability + 0.02 * elapsed)

        # Clarity depends on mood + load
        if "negative" in mood:
            self.clarity = max(0.2, self.clarity - 0.02 * elapsed)
        else:
            self.clarity = min(1.0, self.clarity + 0.015 * elapsed)

        # Random micro-fluctuations
        self.stability = max(0.0, min(1.0, self.stability + random.uniform(-0.01, 0.01)))
        self.clarity = max(0.0, min(1.0, self.clarity + random.uniform(-0.01, 0.01)))

        return {
            "stability": self.stability,
            "clarity": self.clarity,
            "cognitive_load": self.cognitive_load
        }
