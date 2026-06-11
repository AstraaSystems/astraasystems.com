import re

class EmotionClassifier:
    """
    EMOTION CLASSIFIER MODULE
    Maps tone + keywords + intensity into emotional states.
    """

    def __init__(self):
        # Emotion keyword dictionary
        self.emotion_keywords = {
            "anger": ["angry", "furious", "rage", "irritated", "pissed"],
            "sadness": ["sad", "hurt", "crying", "broken", "upset"],
            "fear": ["scared", "afraid", "terrified", "worried", "anxious"],
            "joy": ["happy", "excited", "joyful", "glad", "delighted"],
            "confusion": ["confused", "lost", "uncertain", "unsure"],
            "shame": ["ashamed", "embarrassed", "guilty"],
            "love": ["love", "care", "adore", "appreciate"],
            "neutral": []
        }

        # Intensity cues
        self.intensity_markers = {
            "high": ["very", "extremely", "really", "so", "super"],
            "low": ["kind of", "a little", "slightly"]
        }

    def classify(self, text, tone):
        text_lower = text.lower()

        # 1. Emotion from keywords
        emotion = self._keyword_emotion(text_lower)

        # 2. If tone suggests emotion, merge
        emotion = self._merge_tone_emotion(emotion, tone)

        # 3. Detect intensity
        intensity = self._detect_intensity(text_lower)

        return {
            "emotion": emotion,
            "intensity": intensity
        }

    def _keyword_emotion(self, text):
        for emotion, keywords in self.emotion_keywords.items():
            for word in keywords:
                if re.search(rf"\b{word}\b", text):
                    return emotion
        return "neutral"

    def _merge_tone_emotion(self, emotion, tone):
        if emotion != "neutral":
            return emotion
        if tone in ["anger", "sadness", "fear", "joy", "confusion"]:
            return tone
        return "neutral"

    def _detect_intensity(self, text):
        for marker in self.intensity_markers["high"]:
            if marker in text:
                return "high"
        for marker in self.intensity_markers["low"]:
            if marker in text:
                return "low"
        return "medium"
