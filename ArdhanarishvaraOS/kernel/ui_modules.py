#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  UI Modules — SovereignOS Interface Rendering & Interaction Layer
#  File: ui_modules.py
#===============================================================================

import time
import uuid
import json
import asyncio
from typing import Dict, Any, Callable, Optional

class UIModules:
    """
    Provides:
      • dynamic UI component rendering
      • event dispatching
      • state synchronization
      • kernel-to-UI bridge
      • reactive update propagation
    """

    def __init__(self):
        self.components: Dict[str, Callable[..., Any]] = {}
        self.state: Dict[str, Any] = {}
        self.event_handlers: Dict[str, Callable[..., Any]] = {}

    #---------------------------------------------------------------------------
    #  REGISTER UI COMPONENT
    #---------------------------------------------------------------------------
    def register_component(self, name: str, renderer: Callable[..., Any]):
        self.components[name] = renderer

    #---------------------------------------------------------------------------
    #  REGISTER EVENT HANDLER
    #---------------------------------------------------------------------------
    def register_event(self, event: str, handler: Callable[..., Any]):
        self.event_handlers[event] = handler

    #---------------------------------------------------------------------------
    #  SET UI STATE
    #---------------------------------------------------------------------------
    def set_state(self, key: str, value: Any):
        self.state[key] = value

    #---------------------------------------------------------------------------
    #  GET UI STATE
    #---------------------------------------------------------------------------
    def get_state(self, key: str) -> Any:
        return self.state.get(key)

    #---------------------------------------------------------------------------
    #  RENDER COMPONENT
    #---------------------------------------------------------------------------
    async def render(self, component: str, props: Dict[str, Any]) -> Dict[str, Any]:
        if component not in self.components:
            return {
                "render_id": f"UIR-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_component",
                "timestamp": time.time()
            }

        try:
            output = await self.components[component](props)
            return {
                "render_id": f"UIR-{uuid.uuid4().hex[:10].upper()}",
                "component": component,
                "status": "ok",
                "output": output,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "render_id": f"UIR-{uuid.uuid4().hex[:10].upper()}",
                "component": component,
                "status": "render_error",
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  DISPATCH UI EVENT
    #---------------------------------------------------------------------------
    async def dispatch_event(self, event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if event not in self.event_handlers:
            return {
                "event_id": f"EVT-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_event",
                "timestamp": time.time()
            }

        try:
            result = await self.event_handlers[event](payload)
            return {
                "event_id": f"EVT-{uuid.uuid4().hex[:10].upper()}",
                "event": event,
                "status": "ok",
                "result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "event_id": f"EVT-{uuid.uuid4().hex[:10].upper()}",
                "event": event,
                "status": "event_error",
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  UI STATE SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"UIS-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "state": json.dumps(self.state)
        }

#===============================================================================
#  END OF FILE — ui_modules.py
#===============================================================================
