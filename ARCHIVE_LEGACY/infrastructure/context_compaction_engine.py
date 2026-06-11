# ============================================================
# CONTEXT COMPACTION ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

import time
import threading

class ContextCompactionEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.thresholds = {
            "max_tokens": 32000,
            "min_retain": 8000,
            "aggressive_cut": 0.40
        }
        self.meta = {
            "compactions": 0,
            "last_compaction": 0.0,
            "total_tokens_removed": 0
        }
        self.history = []
        self.limits = {"history":200}

    # ============================================================
    # ANALYZE CONTEXT SIZE
    # ============================================================
    def analyze(self, token_count):
        if token_count > self.thresholds["max_tokens"]:
            return {"compact": True, "reason": "overflow"}
        return {"compact": False}

    # ============================================================
    # COMPACT CONTEXT
    # ============================================================
    def compact(self, context_blocks):
        with self.lock:
            total_tokens = sum(len(block) for block in context_blocks)
            if total_tokens <= self.thresholds["max_tokens"]:
                return {"compacted": False, "context": context_blocks}

            target = int(total_tokens * self.thresholds["aggressive_cut"])
            removed = 0
            new_blocks = []

            for block in context_blocks:
                if removed < target:
                    removed += len(block)
                    continue
                new_blocks.append(block)

            self.meta["compactions"] += 1
            self.meta["last_compaction"] = time.time()
            self.meta["total_tokens_removed"] += removed
            self._log()

            return {"compacted": True, "context": new_blocks, "removed": removed}

    # ============================================================
    # FORCE HARD RESET
    # ============================================================
    def hard_reset(self):
        with self.lock:
            self.meta["compactions"] = 0
            self.meta["total_tokens_removed"] = 0
            self.history = []
            self._log()
            return {"reset": True}

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        entry = {
            "compactions": self.meta["compactions"],
            "removed": self.meta["total_tokens_removed"],
            "ts": time.time()
        }
        self.history.append(entry)
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {
            "meta": self.meta,
            "history": len(self.history),
            "thresholds": self.thresholds
        }
