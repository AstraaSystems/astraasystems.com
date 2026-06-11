# ============================================================
# LUX — ENHANCED COGNITIVE LOOP
# Y‑PRIME EDITION
# ============================================================

import time
import threading

class LuxEnhanced:

    def __init__(self, ipc, reflection_engine, synthesis_engine, compaction_engine):
        self.ipc = ipc
        self.reflector = reflection_engine
        self.synth = synthesis_engine
        self.compactor = compaction_engine

        self.lock = threading.Lock()

        self.memory = {
            "ephemeral": [],
            "structural": [],
            "anchors": [],
            "identity": {
                "tone": "calm",
                "style": "minimalistic",
                "behavior": "clarity",
                "rules": [
                    "seek_essence",
                    "remove_noise",
                    "reveal_structure",
                    "maintain_purity",
                    "illuminate_path"
                ]
            }
        }

        self.channels = {
            "intake": "lux.intake",
            "distill": "lux.distill",
            "illuminate": "lux.illuminate",
            "output": "lux.output"
        }

        self.meta = {
            "cycles": 0,
            "last_cycle": 0.0,
            "distillations": 0,
            "illuminations": 0,
            "anchors": 0
        }

    # ============================================================
    # INTAKE
    # ============================================================
    def intake(self, payload):
        with self.lock:
            self.memory["ephemeral"].append(payload)
            if len(self.memory["ephemeral"]) > 50:
                self.memory["ephemeral"].pop(0)
            return {"received": True}

    # ============================================================
    # COMPRESSION (NOISE REMOVAL)
    # ============================================================
    def compress(self, text):
        words = text.split()
        filtered = [w for w in words if len(w) > 2]
        if len(filtered) <= 20:
            return " ".join(filtered)
        return " ".join(filtered[:20]) + " ..."
    
    # ============================================================
    # DISTILLATION
    # ============================================================
    def distill(self, text):
        compressed = self.compress(text)
        reduced = self._reduce(compressed)

        self.memory["structural"].append(reduced)
        if len(self.memory["structural"]) > 200:
            self.memory["structural"].pop(0)

        self.meta["distillations"] += 1
        return {"distilled": reduced}

    # ============================================================
    # ANCHOR EXTRACTION
    # ============================================================
    def anchor(self, text):
        parts = text.split()
        anchors = [parts[0], parts[len(parts)//2], parts[-1]] if len(parts) >= 3 else parts

        self.memory["anchors"].append(anchors)
        if len(self.memory["anchors"]) > 100:
            self.memory["anchors"].pop(0)

        self.meta["anchors"] += 1
        return {"anchors": anchors}

    # ============================================================
    # ILLUMINATION
    # ============================================================
    def illuminate(self, text):
        distilled = self._reduce(text)
        illuminated = self._extract(distilled)
        anchors = self.anchor(distilled)

        self.meta["illuminations"] += 1
        return {
            "illuminated": illuminated,
            "anchors": anchors["anchors"]
        }

    # ============================================================
    # INTERNAL REDUCTION
    # ============================================================
    def _reduce(self, text):
        words = text.split()
        if len(words) <= 25:
            return text
        return " ".join(words[:25]) + " ..."

    # ============================================================
    # INTERNAL STRUCTURE EXTRACTION
    # ============================================================
    def _extract(self, text):
        parts = text.split()
        if len(parts) < 6:
            return text
        third = len(parts) // 3
        return " | ".join([
            " ".join(parts[:third]),
            " ".join(parts[third:third*2]),
            " ".join(parts[third*2:])
        ])

    # ============================================================
    # FULL COGNITIVE CYCLE
    # ============================================================
    def cycle(self):
        with self.lock:
            if not self.memory["ephemeral"]:
                return {"cycle": False}

            raw = self.memory["ephemeral"][-1]

            compressed = self.compress(raw)
            distilled = self._reduce(compressed)
            illuminated = self._extract(distilled)
            anchors = self.anchor(distilled)["anchors"]

            self.meta["cycles"] += 1
            self.meta["last_cycle"] = time.time()

            self.ipc.publish(self.channels["output"], {
                "distilled": distilled,
                "illuminated": illuminated,
                "anchors": anchors
            })

            return {
                "cycle": True,
                "distilled": distilled,
                "illuminated": illuminated,
                "anchors": anchors
            }

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {
            "meta": self.meta,
            "ephemeral": len(self.memory["ephemeral"]),
            "structural": len(self.memory["structural"]),
            "anchors": len(self.memory["anchors"]),
            "identity": self.memory["identity"]
        }
