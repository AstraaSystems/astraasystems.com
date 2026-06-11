# File: /home/keshanth/ARKA/ardhanarishvara/meta_cognitive/reflection_engine.py
#!/usr/bin/env python3
"""
Reflection Engine
-----------------
Extracts structure, patterns, and meaning from raw text.
"""

class ReflectionEngine:

    def reflect(self, text: str) -> dict:
        words = text.split()
        length = len(words)

        return {
            "original": text,
            "word_count": length,
            "first_10": " ".join(words[:10]),
            "last_10": " ".join(words[-10:]),
            "keywords": self._extract_keywords(words),
        }

    def _extract_keywords(self, words):
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1

        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:5]]
