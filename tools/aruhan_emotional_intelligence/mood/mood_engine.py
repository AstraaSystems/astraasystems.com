class MoodEngine:
    """
    MOOD ENGINE
    Tracks Aruhan's internal emotional baseline over time.
    Supports:
    - dynamic mood drift
    - mood stabilization
    - mood influence from user emotion
    - emotional inertia (slow changes)
    """

    def __init__(self):
        self.mood = "neutral"
        self.stability = 1.0  # higher = slower mood changes
        self.mood_weights = {
            "joy": 1,
            "sadness": -1,
            "anger": -2,
            "fear": -1,
            "confusion": -0.5,
            "neutral": 0
        }

    def update_mood(self, emotion, intensity):
        # Convert intensity to numeric weight
        intensity_factor = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5
        }.get(intensity, 1.0)

        # Determine emotional impact
        impact = self.mood_weights.get(emotion, 0) * intensity_factor

        # Apply stability (emotional inertia)
        adjusted_impact = impact / max(self.stability, 0.1)

        # Update mood value
        new_value = self._mood_to_value(self.mood) + adjusted_impact

        # Clamp mood value
        new_value = max(-5, min(5, new_value))

        # Convert back to mood label
        self.mood = self._value_to_mood(new_value)

        return self.mood

    def _mood_to_value(self, mood):
        mapping = {
            "very_negative": -5,
            "negative": -3,
            "slightly_negative": -1,
            "neutral": 0,
            "slightly_positive": 1,
            "positive": 3,
            "very_positive": 5
        }
        return mapping.get(mood, 0)

    def _value_to_mood(self, value):
        if value <= -4:
            return "very_negative"
        if value <= -2:
            return "negative"
        if value < 0:
            return "slightly_negative"
        if value == 0:
            return "neutral"
        if value <= 2:
            return "slightly_positive"
        if value <= 4:
            return "positive"
        return "very_positive"

    def get_mood(self):
        return self.mood
