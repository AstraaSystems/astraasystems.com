# File: /home/keshanth/ARKA/ardhanarishvara/meta_cognitive/synthesis_engine.py
#!/usr/bin/env python3
"""
Synthesis Engine
----------------
Combines multiple reflections into a single structured summary.
"""

class SynthesisEngine:

    def synthesize(self, reflections: list) -> dict:
        if not reflections:
            return {"summary": "", "keywords": []}

        combined = " ".join([r["original"] for r in reflections])
        all_keywords = []

        for r in reflections:
            all_keywords.extend(r.get("keywords", []))

        top_keywords = self._top(all_keywords)

        return {
            "summary": combined[:300] + ("..." if len(combined) > 300 else ""),
            "keywords": top_keywords,
        }

    def _top(self, items):
        freq = {}
        for i in items:
            freq[i] = freq.get(i, 0) + 1

        sorted_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_items[:5]]
