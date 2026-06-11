#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Clock & Timing Engine — System Clock, Timers & Scheduler Signals
#  File: clock_timing_engine.py
#===============================================================================

import time
import uuid
import asyncio
from typing import Dict, Any, Callable, List

class ClockTimingEngine:
    """
    Provides:
      • system monotonic clock
      • high‑precision timers
      • repeating intervals
      • scheduler tick signals
      • kernel‑level timing telemetry
    """

    def __init__(self):
        self.timers: Dict[str, Dict[str, Any]] = {}
        self.intervals: Dict[str, Dict[str, Any]] = {}
        self.telemetry: Dict[str, Any] = {
            "ticks": 0,
            "timers_fired": 0,
            "intervals_fired": 0
        }
        self.tick_interval = 0.01  # 10ms scheduler tick

    #---------------------------------------------------------------------------
    #  SYSTEM CLOCK
    #---------------------------------------------------------------------------
    def now(self) -> float:
        return time.time()

    def monotonic(self) -> float:
        return time.monotonic()

    #---------------------------------------------------------------------------
    #  CREATE ONE‑SHOT TIMER
    #---------------------------------------------------------------------------
    def timer(self, delay: float, handler: Callable[..., Any]) -> str:
        tid = f"TMR-{uuid.uuid4().hex[:10].upper()}"
        self.timers[tid] = {
            "id": tid,
            "delay": delay,
            "handler": handler,
            "created": time.time(),
            "fires_at": time.time() + delay
        }
        return tid

    #---------------------------------------------------------------------------
    #  CREATE INTERVAL TIMER
    #---------------------------------------------------------------------------
    def interval(self, every: float, handler: Callable[..., Any]) -> str:
        iid = f"INT-{uuid.uuid4().hex[:10].upper()}"
        self.intervals[iid] = {
            "id": iid,
            "every": every,
            "handler": handler,
            "last_fire": time.time()
        }
        return iid

    #---------------------------------------------------------------------------
    #  CANCEL TIMER / INTERVAL
    #---------------------------------------------------------------------------
    def cancel(self, timer_id: str):
        if timer_id in self.timers:
            del self.timers[timer_id]
        if timer_id in self.intervals:
            del self.intervals[timer_id]

    #---------------------------------------------------------------------------
    #  INTERNAL: FIRE TIMERS
    #---------------------------------------------------------------------------
    async def _process_timers(self):
        now = time.time()
        fired = []

        for tid, t in list(self.timers.items()):
            if now >= t["fires_at"]:
                try:
                    await t["handler"]()
                except:
                    pass
                fired.append(tid)
                self.telemetry["timers_fired"] += 1

        for tid in fired:
            del self.timers[tid]

    #---------------------------------------------------------------------------
    #  INTERNAL: FIRE INTERVALS
    #---------------------------------------------------------------------------
    async def _process_intervals(self):
        now = time.time()

        for iid, iv in self.intervals.items():
            if now - iv["last_fire"] >= iv["every"]:
                try:
                    await iv["handler"]()
                except:
                    pass
                iv["last_fire"] = now
                self.telemetry["intervals_fired"] += 1

    #---------------------------------------------------------------------------
    #  SCHEDULER TICK LOOP
    #---------------------------------------------------------------------------
    async def run(self):
        while True:
            self.telemetry["ticks"] += 1
            await self._process_timers()
            await self._process_intervals()
            await asyncio.sleep(self.tick_interval)

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"CLK-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "timers": self.timers,
            "intervals": self.intervals,
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — clock_timing_engine.py
#===============================================================================
