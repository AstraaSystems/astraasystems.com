#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  App Runtime Engine — SovereignOS Application Execution, Lifecycle & IPC Core
#  File: app_runtime_engine.py
#===============================================================================

import time
import uuid
import asyncio
from typing import Dict, Any, Callable, Optional

class AppRuntimeEngine:
    """
    Provides:
      • application lifecycle management
      • async execution sandbox
      • inter‑process communication (IPC)
      • app state persistence
      • kernel‑level runtime orchestration
    """

    def __init__(self):
        self.apps: Dict[str, Dict[str, Any]] = {}
        self.ipc_channels: Dict[str, Callable[..., Any]] = {}

    #---------------------------------------------------------------------------
    #  REGISTER APP EXECUTOR
    #---------------------------------------------------------------------------
    def register_executor(self, app_id: str, executor: Callable[..., Any]):
        self.apps[app_id] = {
            "executor": executor,
            "state": {},
            "running": False,
            "last_run": None
        }

    #---------------------------------------------------------------------------
    #  START APP
    #---------------------------------------------------------------------------
    async def start(self, app_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if app_id not in self.apps:
            return {
                "runtime_id": f"RTM-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_app",
                "timestamp": time.time()
            }

        app = self.apps[app_id]
        app["running"] = True
        app["last_run"] = time.time()

        try:
            result = await app["executor"](payload)
            return {
                "runtime_id": f"RTM-{uuid.uuid4().hex[:10].upper()}",
                "app_id": app_id,
                "status": "completed",
                "result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            app["running"] = False
            return {
                "runtime_id": f"RTM-{uuid.uuid4().hex[:10].upper()}",
                "app_id": app_id,
                "status": "runtime_error",
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  STOP APP
    #---------------------------------------------------------------------------
    def stop(self, app_id: str):
        if app_id in self.apps:
            self.apps[app_id]["running"] = False

    #---------------------------------------------------------------------------
    #  SET APP STATE
    #---------------------------------------------------------------------------
    def set_state(self, app_id: str, key: str, value: Any):
        if app_id in self.apps:
            self.apps[app_id]["state"][key] = value

    #---------------------------------------------------------------------------
    #  GET APP STATE
    #---------------------------------------------------------------------------
    def get_state(self, app_id: str, key: str) -> Any:
        if app_id in self.apps:
            return self.apps[app_id]["state"].get(key)
        return None

    #---------------------------------------------------------------------------
    #  REGISTER IPC CHANNEL
    #---------------------------------------------------------------------------
    def register_ipc(self, channel: str, handler: Callable[..., Any]):
        self.ipc_channels[channel] = handler

    #---------------------------------------------------------------------------
    #  SEND IPC MESSAGE
    #---------------------------------------------------------------------------
    async def ipc(self, channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if channel not in self.ipc_channels:
            return {
                "ipc_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_channel",
                "timestamp": time.time()
            }

        try:
            result = await self.ipc_channels[channel](payload)
            return {
                "ipc_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
                "channel": channel,
                "status": "ok",
                "result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "ipc_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
                "channel": channel,
                "status": "ipc_error",
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  RUNTIME SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"RTS-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "apps": self.apps
        }

#===============================================================================
#  END OF FILE — app_runtime_engine.py
#===============================================================================
