# ============================================================
# METACOGNITIVE REFLECTION ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

import time
import threading

class MetacognitiveReflectionEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.reflections = []
        self.thresholds = {
            "max_reflections": 50,
            "min_interval": 2.0
        }
        self.meta = {
            "total_reflections": 0,
            "last_reflection": 0.0
        }

    # ============================================================
    # REFLECT ON OUTPUT
    # ============================================================
    def reflect(self, output_text):
        now = time.time()
        if now - self.meta["last_reflection"] < self.thresholds["min_interval"]:
            return {"reflected": False, "reason": "interval_limit"}

        with self.lock:
            summary = self._summarize(output_text)
            self.reflections.append(summary)
            self.meta["total_reflections"] += 1
            self.meta["last_reflection"] = now

            if len(self.reflections) > self.thresholds["max_reflections"]:
                self.reflections.pop(0)

            return {"reflected": True, "summary": summary}

    # ============================================================
    # INTERNAL SUMMARIZER
    # ============================================================
    def _summarize(self, text):
        words = text.split()
        if len(words) <= 20:
            return text
        return " ".join(words[:20]) + " ..."

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {
            "meta": self.meta,
            "reflections": len(self.reflections)
        }
