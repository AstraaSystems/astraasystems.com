# File: /home/keshanth/ARKA/ardhanarishvara/meta_cognitive/meta_loop.py
#!/usr/bin/env python3
"""
Meta Loop
---------
Coordinates reflection → synthesis → compaction cycles.
"""

import time

from meta_cognitive.reflection_engine import ReflectionEngine
from meta_cognitive.synthesis_engine import SynthesisEngine
from meta_cognitive.compaction_engine import CompactionEngine


class MetaLoop:

    def __init__(self):
        self.reflector = ReflectionEngine()
        self.synth = SynthesisEngine()
        self.compactor = CompactionEngine()

        self.memory = []
        self.meta = {
            "cycles": 0,
            "last_cycle": 0.0
        }

    def cycle(self, text: str) -> dict:
        reflection = self.reflector.reflect(text)
        self.memory.append(reflection)

        synthesis = self.synth.synthesize(self.memory[-5:])
        compacted = self.compactor.compact(synthesis["summary"])

        self.meta["cycles"] += 1
        self.meta["last_cycle"] = time.time()

        return {
            "reflection": reflection,
            "synthesis": synthesis,
            "compacted": compacted,
            "meta": self.meta
        }
