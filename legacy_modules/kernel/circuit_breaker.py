#!/usr/bin/env python3
# ============================================================
#  CIRCUIT BREAKER v17 — Arka Pillai Holdings Ltd
#  Protects system from failing engines
# ============================================================

import time

class CircuitBreaker:

    def __init__(self):
        self.failures = {}
        self.cooldown = {}

    def record_failure(self, engine_name):
        now = time.time()
        self.failures.setdefault(engine_name, 0)
        self.failures[engine_name] += 1

        if self.failures[engine_name] >= 3:
            self.cooldown[engine_name] = now + 300  # 5 min cooldown

    def is_blocked(self, engine_name):
        if engine_name not in self.cooldown:
            return False
        return time.time() < self.cooldown[engine_name]
