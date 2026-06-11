#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS System Services Engine — Daemon Manager, Service Graph & IPC Core
#  File: system_services_engine.py
#===============================================================================

import time
import uuid
import asyncio
from typing import Dict, Any, List, Callable, Optional

class SystemServicesEngine:
    """
    Provides:
      • service registration
      • dependency graph resolution
      • async daemon lifecycle management
      • service health tracking
      • IPC-based service invocation
    """

    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}
        self.running: Dict[str, Dict[str, Any]] = {}
        self.ipc_handlers: Dict[str, Callable[..., Any]] = {}

    #---------------------------------------------------------------------------
    #  REGISTER SERVICE
    #---------------------------------------------------------------------------
    def register(self, name: str, handler: Callable[..., Any], deps: List[str]):
        self.services[name] = {
            "name": name,
            "handler": handler,
            "dependencies": deps,
            "running": False,
            "last_start": None,
            "health": "unknown"
        }

    #---------------------------------------------------------------------------
    #  RESOLVE DEPENDENCIES
    #---------------------------------------------------------------------------
    def resolve(self, name: str, visited=None) -> List[str]:
        if visited is None:
            visited = set()

        if name not in self.services:
            return []

        if name in visited:
            return []

        visited.add(name)
        deps = self.services[name]["dependencies"]
        resolved = []

        for d in deps:
            resolved.extend(self.resolve(d, visited))
            resolved.append(d)

        return list(dict.fromkeys(resolved))

    #---------------------------------------------------------------------------
    #  START SERVICE
    #---------------------------------------------------------------------------
    async def start(self, name: str) -> Dict[str, Any]:
        if name not in self.services:
            return {
                "service_id": f"SVC-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_service",
                "timestamp": time.time()
            }

        deps = self.resolve(name)
        for d in deps:
            if not self.services[d]["running"]:
                await self._launch(d)

        return await self._launch(name)

    #---------------------------------------------------------------------------
    #  INTERNAL LAUNCH
    #---------------------------------------------------------------------------
    async def _launch(self, name: str) -> Dict[str, Any]:
        svc = self.services[name]

        try:
            task = asyncio.create_task(svc["handler"]())
            self.running[name] = {
                "task": task,
                "start_time": time.time()
            }
            svc["running"] = True
            svc["last_start"] = time.time()
            svc["health"] = "running"

            return {
                "service_id": f"SVC-{uuid.uuid4().hex[:10].upper()}",
                "status": "started",
                "service": name,
                "timestamp": time.time()
            }

        except Exception as e:
            svc["health"] = "failed"
            return {
                "service_id": f"SVC-{uuid.uuid4().hex[:10].upper()}",
                "status": "start_error",
                "service": name,
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  STOP SERVICE
    #---------------------------------------------------------------------------
    def stop(self, name: str) -> Dict[str, Any]:
        if name not in self.services or name not in self.running:
            return {
                "service_id": f"SVC-{uuid.uuid4().hex[:10].upper()}",
                "status": "not_running",
                "timestamp": time.time()
            }

        task = self.running[name]["task"]
        task.cancel()

        del self.running[name]
        self.services[name]["running"] = False
        self.services[name]["health"] = "stopped"

        return {
            "service_id": f"SVC-{uuid.uuid4().hex[:10].upper()}",
            "status": "stopped",
            "service": name,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  REGISTER IPC CHANNEL
    #---------------------------------------------------------------------------
    def register_ipc(self, channel: str, handler: Callable[..., Any]):
        self.ipc_handlers[channel] = handler

    #---------------------------------------------------------------------------
    #  SEND IPC MESSAGE
    #---------------------------------------------------------------------------
    async def ipc(self, channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if channel not in self.ipc_handlers:
            return {
                "ipc_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_channel",
                "timestamp": time.time()
            }

        try:
            result = await self.ipc_handlers[channel](payload)
            return {
                "ipc_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
                "status": "ok",
                "channel": channel,
                "result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "ipc_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
                "status": "ipc_error",
                "channel": channel,
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"SYS-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "services": self.services,
            "running": list(self.running.keys())
        }

#===============================================================================
#  END OF FILE — system_services_engine.py
#===============================================================================
