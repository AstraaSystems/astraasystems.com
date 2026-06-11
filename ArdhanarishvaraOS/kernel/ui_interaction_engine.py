#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  UI Interaction Engine — SovereignOS Event, Gesture & Input Processing Core
#  File: ui_interaction_engine.py
#===============================================================================

import time
import uuid
import asyncio
from typing import Dict, Any, Callable, Optional, List

class UIInteractionEngine:
    """
    Provides:
      • event routing
      • gesture interpretation
      • input normalization
      • interaction state tracking
      • async UI event pipelines
    """

    def __init__(self):
        self.handlers: Dict[str, Callable[..., Any]] = {}
        self.gestures: Dict[str, Callable[..., Any]] = {}
        self.interaction_state: Dict[str, Any] = {}

    #---------------------------------------------------------------------------
    #  REGISTER EVENT HANDLER
    #---------------------------------------------------------------------------
    def register_event(self, event: str, handler: Callable[..., Any]):
        self.handlers[event] = handler

    #---------------------------------------------------------------------------
    #  REGISTER GESTURE
    #---------------------------------------------------------------------------
    def register_gesture(self, gesture: str, handler: Callable[..., Any]):
        self.gestures[gesture] = handler

    #---------------------------------------------------------------------------
    #  UPDATE INTERACTION STATE
    #---------------------------------------------------------------------------
    def set_state(self, key: str, value: Any):
        self.interaction_state[key] = value

    #---------------------------------------------------------------------------
    #  GET INTERACTION STATE
    #---------------------------------------------------------------------------
    def get_state(self, key: str) -> Any:
        return self.interaction_state.get(key)

    #---------------------------------------------------------------------------
    #  NORMALIZE INPUT
    #---------------------------------------------------------------------------
    def _normalize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "x": float(payload.get("x", 0)),
            "y": float(payload.get("y", 0)),
            "pressure": float(payload.get("pressure", 0)),
            "meta": payload.get("meta", {})
        }

    #---------------------------------------------------------------------------
    #  PROCESS EVENT
    #---------------------------------------------------------------------------
    async def process_event(self, event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if event not in self.handlers:
            return {
                "interaction_id": f"INT-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_event",
                "timestamp": time.time()
            }

        normalized = self._normalize(payload)

        try:
            result = await self.handlers[event](normalized)
            return {
                "interaction_id": f"INT-{uuid.uuid4().hex[:10].upper()}",
                "event": event,
                "status": "ok",
                "result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "interaction_id": f"INT-{uuid.uuid4().hex[:10].upper()}",
                "event": event,
                "status": "event_error",
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  PROCESS GESTURE
    #---------------------------------------------------------------------------
    async def process_gesture(self, gesture: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if gesture not in self.gestures:
            return {
                "gesture_id": f"GST-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_gesture",
                "timestamp": time.time()
            }

        normalized = self._normalize(payload)

        try:
            result = await self.gestures[gesture](normalized)
            return {
                "gesture_id": f"GST-{uuid.uuid4().hex[:10].upper()}",
                "gesture": gesture,
                "status": "ok",
                "result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "gesture_id": f"GST-{uuid.uuid4().hex[:10].upper()}",
                "gesture": gesture,
                "status": "gesture_error",
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  BATCH INTERACTION PROCESSING
    #---------------------------------------------------------------------------
    async def batch(self, interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for item in interactions:
            if "event" in item:
                r = await self.process_event(item["event"], item.get("payload", {}))
            else:
                r = await self.process_gesture(item["gesture"], item.get("payload", {}))
            results.append(r)
        return results

#===============================================================================
#  END OF FILE — ui_interaction_engine.py
#===============================================================================
