#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Distributed Node Engine — Cluster, Heartbeats & Replication Core
#  File: distributed_node_engine.py
#===============================================================================

import time
import uuid
import asyncio
from typing import Dict, Any, Optional, Callable, List

class DistributedNodeEngine:
    """
    Provides:
      • node identity & registration
      • cluster membership management
      • heartbeat monitoring
      • distributed message replication
      • consensus-ready event hooks
      • distributed telemetry
    """

    def __init__(self):
        self.node_id = f"NODE-{uuid.uuid4().hex[:10].upper()}"
        self.cluster: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable[..., Any]] = {}
        self.telemetry: Dict[str, Any] = {
            "messages_sent": 0,
            "messages_received": 0,
            "heartbeats_sent": 0,
            "heartbeats_received": 0,
            "nodes_joined": 0,
            "nodes_left": 0,
            "errors": 0
        }
        self.heartbeat_interval = 2.0
        self.last_heartbeat: Dict[str, float] = {}

    #---------------------------------------------------------------------------
    #  REGISTER NODE IN CLUSTER
    #---------------------------------------------------------------------------
    def join_cluster(self, address: str) -> Dict[str, Any]:
        nid = f"ND-{uuid.uuid4().hex[:10].upper()}"
        self.cluster[nid] = {
            "id": nid,
            "address": address,
            "joined": time.time(),
            "last_heartbeat": None
        }
        self.telemetry["nodes_joined"] += 1
        return self.cluster[nid]

    #---------------------------------------------------------------------------
    #  REMOVE NODE
    #---------------------------------------------------------------------------
    def leave_cluster(self, node_id: str) -> Dict[str, Any]:
        if node_id not in self.cluster:
            self.telemetry["errors"] += 1
            return {
                "leave_id": f"LEV-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_node",
                "timestamp": time.time()
            }

        del self.cluster[node_id]
        self.telemetry["nodes_left"] += 1

        return {
            "leave_id": f"LEV-{uuid.uuid4().hex[:10].upper()}",
            "status": "removed",
            "node": node_id,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  REGISTER MESSAGE HANDLER
    #---------------------------------------------------------------------------
    def register_handler(self, name: str, handler: Callable[..., Any]):
        self.handlers[name] = handler

    #---------------------------------------------------------------------------
    #  SEND MESSAGE TO NODE
    #---------------------------------------------------------------------------
    async def send(self, node_id: str, handler: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if node_id not in self.cluster:
            self.telemetry["errors"] += 1
            return {
                "msg_id": f"DST-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_node",
                "timestamp": time.time()
            }

        if handler not in self.handlers:
            self.telemetry["errors"] += 1
            return {
                "msg_id": f"DST-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_handler",
                "timestamp": time.time()
            }

        try:
            result = await self.handlers[handler](payload)
            self.telemetry["messages_sent"] += 1
            self.telemetry["messages_received"] += 1

            return {
                "msg_id": f"DST-{uuid.uuid4().hex[:10].upper()}",
                "status": "ok",
                "node": node_id,
                "handler": handler,
                "result": result,
                "timestamp": time.time()
            }

        except Exception as e:
            self.telemetry["errors"] += 1
            return {
                "msg_id": f"DST-{uuid.uuid4().hex[:10].upper()}",
                "status": "handler_error",
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  BROADCAST MESSAGE
    #---------------------------------------------------------------------------
    async def broadcast(self, handler: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        responses = []
        for nid in list(self.cluster.keys()):
            res = await self.send(nid, handler, payload)
            responses.append(res)

        return {
            "broadcast_id": f"BRC-{uuid.uuid4().hex[:10].upper()}",
            "status": "completed",
            "responses": responses,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  HEARTBEAT LOOP
    #---------------------------------------------------------------------------
    async def heartbeat_loop(self):
        while True:
            for nid in self.cluster:
                self.last_heartbeat[nid] = time.time()
                self.telemetry["heartbeats_sent"] += 1
            await asyncio.sleep(self.heartbeat_interval)

    #---------------------------------------------------------------------------
    #  RECEIVE HEARTBEAT
    #---------------------------------------------------------------------------
    def heartbeat(self, node_id: str):
        if node_id in self.cluster:
            self.cluster[node_id]["last_heartbeat"] = time.time()
            self.telemetry["heartbeats_received"] += 1

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"DNE-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "node_id": self.node_id,
            "cluster": self.cluster,
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — distributed_node_engine.py
#===============================================================================
