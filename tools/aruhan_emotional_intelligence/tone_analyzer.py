import re

class ToneAnalyzer:
    """
    TONE ANALYZER MODULE
    Lightweight rule-based tone detection for Aruhan Core.
    """

    def __init__(self):
        # Keyword dictionaries for tone detection
        self.tone_keywords = {
            "anger": ["angry", "mad", "furious", "pissed", "annoyed", "irritated"],
            "sadness": ["sad", "upset", "depressed", "down", "hurt", "heartbroken"],
            "fear": ["scared", "afraid", "worried", "anxious", "nervous", "terrified"],
            "joy": ["happy", "excited", "glad", "joyful", "great", "amazing"],
            "confusion": ["confused", "lost", "unsure", "uncertain", "puzzled"],
            "neutral": []
        }

        # Punctuation-based tone cues
        self.punctuation_cues = {
            "anger": ["!!!", "!?"],
            "excitement": ["!!"],
            "uncertainty": ["...?"],
            "sadness": ["..."]
        }

    def analyze(self, text):
        text_lower = text.lower()

        # 1. Keyword-based tone detection
        keyword_tone = self._keyword_tone(text_lower)

        # 2. Punctuation-based tone detection
        punctuation_tone = self._punctuation_tone(text)

        # 3. Merge tones
        final_tone = self._merge_tones(keyword_tone, punctuation_tone)

        return {
            "tone": final_tone,
            "keyword_tone": keyword_tone,
            "punctuation_tone": punctuation_tone
        }

    def _keyword_tone(self, text):
        for tone, keywords in self.tone_keywords.items():
            for word in keywords:
                if re.search(rf"\b{word}\b", text):
                    return tone
        return "neutral"

    def _punctuation_tone(self, text):
        for tone, cues in self.punctuation_cues.items():
            for cue in cues:
                if cue in text:
                    return tone
        return None

    def _merge_tones(self, keyword_tone, punctuation_tone):
        if keyword_tone != "neutral":
            return keyword_tone
        if punctuation_tone:
            return punctuation_tone
        return "neutral"
