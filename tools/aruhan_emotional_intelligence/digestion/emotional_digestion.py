import time
import math

class EmotionalDigestionEngine:
    """
    EMOTIONAL DIGESTION ENGINE
    Non-linear cognitive latency system.
    Simulates:
    - emotional processing delay
    - cognitive load
    - emotional residue
    - digestion curve (logarithmic decay)
    """

    def __init__(self):
        self.residue = 0.0  # emotional leftover
        self.last_update = time.time()

    def ingest(self, emotion, intensity):
        # Convert emotion to numeric weight
        emotion_weights = {
            "anger": 3.0,
            "sadness": 2.0,
            "fear": 2.5,
            "confusion": 1.5,
            "joy": 1.0,
            "neutral": 0.5
        }

        intensity_factor = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5
        }.get(intensity, 1.0)

        # Add emotional residue
        self.residue += emotion_weights.get(emotion, 1.0) * intensity_factor

    def digest(self):
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Logarithmic decay curve
        if self.residue > 0:
            decay = math.log(1 + elapsed) * 0.5
            self.residue = max(0, self.residue - decay)

        # Latency factor increases with residue
        latency = 1.0 + min(self.residue / 5.0, 2.0)

        return latency

    def get_residue(self):
        return self.residue
