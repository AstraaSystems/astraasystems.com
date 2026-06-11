#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  UI Animation Engine — SovereignOS Timeline, Keyframe & Motion Engine
#  File: ui_animation_engine.py
#===============================================================================

import time
import uuid
import asyncio
import math
from typing import Dict, Any, List, Callable

class UIAnimationEngine:
    """
    Provides:
      • keyframe animation
      • timeline scheduling
      • easing functions
      • async animation pipelines
      • kernel-driven motion orchestration
    """

    def __init__(self):
        self.animations: Dict[str, Dict[str, Any]] = {}
        self.easing_functions: Dict[str, Callable[[float], float]] = {
            "linear": lambda t: t,
            "ease_in": lambda t: t * t,
            "ease_out": lambda t: 1 - (1 - t) * (1 - t),
            "ease_in_out": lambda t: 0.5 * (math.sin((t - 0.5) * math.pi) + 1)
        }

    #---------------------------------------------------------------------------
    #  REGISTER ANIMATION
    #---------------------------------------------------------------------------
    def register(self, name: str, keyframes: List[Dict[str, Any]], duration: float, easing: str = "linear"):
        self.animations[name] = {
            "keyframes": keyframes,
            "duration": duration,
            "easing": easing
        }

    #---------------------------------------------------------------------------
    #  INTERPOLATE BETWEEN TWO KEYFRAMES
    #---------------------------------------------------------------------------
    def _interpolate(self, start: Dict[str, Any], end: Dict[str, Any], t: float) -> Dict[str, Any]:
        result = {}
        for k in start:
            if isinstance(start[k], (int, float)) and isinstance(end.get(k), (int, float)):
                result[k] = start[k] + (end[k] - start[k]) * t
            else:
                result[k] = end.get(k, start[k])
        return result

    #---------------------------------------------------------------------------
    #  RESOLVE KEYFRAME AT TIME t
    #---------------------------------------------------------------------------
    def _resolve(self, keyframes: List[Dict[str, Any]], t: float) -> Dict[str, Any]:
        if t <= keyframes[0]["t"]:
            return keyframes[0]["values"]
        if t >= keyframes[-1]["t"]:
            return keyframes[-1]["values"]

        for i in range(len(keyframes) - 1):
            a = keyframes[i]
            b = keyframes[i + 1]
            if a["t"] <= t <= b["t"]:
                local_t = (t - a["t"]) / (b["t"] - a["t"])
                return self._interpolate(a["values"], b["values"], local_t)

        return keyframes[-1]["values"]

    #---------------------------------------------------------------------------
    #  PLAY ANIMATION
    #---------------------------------------------------------------------------
    async def play(self, name: str, callback: Callable[[Dict[str, Any]], Any]) -> Dict[str, Any]:
        if name not in self.animations:
            return {
                "animation_id": f"ANI-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_animation",
                "timestamp": time.time()
            }

        anim = self.animations[name]
        duration = anim["duration"]
        keyframes = anim["keyframes"]
        easing = self.easing_functions.get(anim["easing"], self.easing_functions["linear"])

        start_time = time.time()

        while True:
            now = time.time()
            elapsed = now - start_time
            t = min(1.0, elapsed / duration)
            eased = easing(t)

            frame = self._resolve(keyframes, eased)
            await callback(frame)

            if t >= 1.0:
                break

            await asyncio.sleep(0.016)  # ~60fps

        return {
            "animation_id": f"ANI-{uuid.uuid4().hex[:10].upper()}",
            "status": "completed",
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  PREVIEW ANIMATION (STATIC)
    #---------------------------------------------------------------------------
    def preview(self, name: str, samples: int = 10) -> List[Dict[str, Any]]:
        if name not in self.animations:
            return []

        anim = self.animations[name]
        keyframes = anim["keyframes"]
        easing = self.easing_functions.get(anim["easing"], self.easing_functions["linear"])

        frames = []
        for i in range(samples):
            t = i / (samples - 1)
            eased = easing(t)
            frames.append(self._resolve(keyframes, eased))

        return frames

#===============================================================================
#  END OF FILE — ui_animation_engine.py
#===============================================================================
