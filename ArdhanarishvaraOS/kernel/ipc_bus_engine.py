#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS IPC Bus Engine — Channels, Routing, Messaging & Async Dispatch
#  File: ipc_bus_engine.py
#===============================================================================

import time
import uuid
import asyncio
from typing import Dict, Any, Callable, List, Optional

class IPCBusEngine:
    """
    Provides:
      • IPC channel registration
      • message routing
      • async request/response
      • broadcast messaging
      • kernel-level IPC telemetry
    """

    def __init__(self):
        self.channels: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable[..., Any]] = {}
        self.telemetry: Dict[str, Any] = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0
        }

    #---------------------------------------------------------------------------
    #  REGISTER CHANNEL
    #---------------------------------------------------------------------------
    def register_channel(self, name: str, handler: Callable[..., Any]):
        cid = f"CHN-{uuid.uuid4().hex[:10].upper()}"
        self.channels[name] = {
            "id": cid,
            "name": name,
            "handler": handler,
            "timestamp": time.time()
        }
        self.handlers[name] = handler
        return cid

    #---------------------------------------------------------------------------
    #  SEND MESSAGE
    #---------------------------------------------------------------------------
    async def send(self, channel: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if channel not in self.handlers:
            self.telemetry["errors"] += 1
            return {
                "msg_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_channel",
                "timestamp": time.time()
            }

        handler = self.handlers[channel]

        try:
            self.telemetry["messages_sent"] += 1
            result = await handler(payload)
            self.telemetry["messages_received"] += 1

            return {
                "msg_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
                "status": "ok",
                "channel": channel,
                "result": result,
                "timestamp": time.time()
            }

        except Exception as e:
            self.telemetry["errors"] += 1
            return {
                "msg_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
                "status": "handler_error",
                "channel": channel,
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  BROADCAST MESSAGE
    #---------------------------------------------------------------------------
    async def broadcast(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        responses = []
        for name, handler in self.handlers.items():
            try:
                result = await handler(payload)
                responses.append({
                    "channel": name,
                    "result": result
                })
                self.telemetry["messages_received"] += 1
            except Exception as e:
                responses.append({
                    "channel": name,
                    "error": str(e)
                })
                self.telemetry["errors"] += 1

        self.telemetry["messages_sent"] += len(self.handlers)

        return {
            "broadcast_id": f"BRC-{uuid.uuid4().hex[:10].upper()}",
            "status": "completed",
            "responses": responses,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  REMOVE CHANNEL
    #---------------------------------------------------------------------------
    def remove_channel(self, name: str) -> Dict[str, Any]:
        if name not in self.channels:
            return {
                "remove_id": f"REM-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_channel",
                "timestamp": time.time()
            }

        del self.channels[name]
        del self.handlers[name]

        return {
            "remove_id": f"REM-{uuid.uuid4().hex[:10].upper()}",
            "status": "removed",
            "channel": name,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  IPC SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"IPC-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "channels": self.channels,
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — ipc_bus_engine.py
#===============================================================================
