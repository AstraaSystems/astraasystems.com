# ============================================================
# ABSTRACT SYNTHESIS ENGINE — Y‑PRIME EDITION
# ============================================================

import threading
import time

class AbstractSynthesisEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.history = []
        self.limits = {"history": 100}

    # ============================================================
    # SYNTHESIZE ABSTRACT REPRESENTATION
    # ============================================================
    def synthesize(self, blocks):
        with self.lock:
            combined = " ".join(blocks)
            abstract = self._reduce(combined)
            self.history.append({"abstract": abstract, "ts": time.time()})
            if len(self.history) > self.limits["history"]:
                self.history.pop(0)
            return {"abstract": abstract}

    # ============================================================
    # INTERNAL REDUCTION
    # ============================================================
    def _reduce(self, text):
        words = text.split()
        if len(words) <= 30:
            return text
        return " ".join(words[:30]) + " ..."

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {"history": len(self.history)}
