#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Networking Engine — Sockets, Routing, Protocol Stack & Net IPC
#  File: networking_engine.py
#===============================================================================

import time
import uuid
import asyncio
import socket
from typing import Dict, Any, Optional, Callable, List

class NetworkingEngine:
    """
    Provides:
      • async socket management
      • routing table engine
      • protocol handlers (TCP/UDP/custom)
      • network service registry
      • kernel-level network event dispatch
    """

    def __init__(self):
        self.routes: Dict[str, str] = {}
        self.services: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable[..., Any]] = {}
        self.active_sockets: Dict[str, Any] = {}

    #---------------------------------------------------------------------------
    #  REGISTER ROUTE
    #---------------------------------------------------------------------------
    def add_route(self, destination: str, gateway: str):
        self.routes[destination] = gateway

    #---------------------------------------------------------------------------
    #  RESOLVE ROUTE
    #---------------------------------------------------------------------------
    def resolve(self, destination: str) -> Optional[str]:
        return self.routes.get(destination)

    #---------------------------------------------------------------------------
    #  REGISTER NETWORK SERVICE
    #---------------------------------------------------------------------------
    def register_service(self, name: str, port: int, protocol: str, handler: Callable[..., Any]):
        self.services[name] = {
            "name": name,
            "port": port,
            "protocol": protocol,
            "handler": handler,
            "active": False
        }

    #---------------------------------------------------------------------------
    #  START SERVICE
    #---------------------------------------------------------------------------
    async def start_service(self, name: str) -> Dict[str, Any]:
        if name not in self.services:
            return {
                "service_id": f"NET-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_service",
                "timestamp": time.time()
            }

        svc = self.services[name]
        protocol = svc["protocol"]
        port = svc["port"]

        try:
            if protocol == "tcp":
                server = await asyncio.start_server(
                    lambda r, w: self._tcp_handler(name, r, w),
                    "0.0.0.0",
                    port
                )
                self.active_sockets[name] = server

            elif protocol == "udp":
                loop = asyncio.get_running_loop()
                transport, protocol_obj = await loop.create_datagram_endpoint(
                    lambda: self._udp_handler(name),
                    local_addr=("0.0.0.0", port)
                )
                self.active_sockets[name] = transport

            svc["active"] = True

            return {
                "service_id": f"NET-{uuid.uuid4().hex[:10].upper()}",
                "status": "started",
                "service": name,
                "timestamp": time.time()
            }

        except Exception as e:
            return {
                "service_id": f"NET-{uuid.uuid4().hex[:10].upper()}",
                "status": "start_error",
                "service": name,
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  TCP HANDLER
    #---------------------------------------------------------------------------
    async def _tcp_handler(self, name: str, reader, writer):
        svc = self.services[name]
        handler = svc["handler"]

        try:
            data = await reader.read(4096)
            response = await handler(data)
            writer.write(response)
            await writer.drain()
        except:
            pass
        finally:
            writer.close()

    #---------------------------------------------------------------------------
    #  UDP HANDLER
    #---------------------------------------------------------------------------
    class _udp_handler(asyncio.DatagramProtocol):
        def __init__(self, name):
            self.name = name

        def datagram_received(self, data, addr):
            pass  # Placeholder for custom UDP logic

    #---------------------------------------------------------------------------
    #  STOP SERVICE
    #---------------------------------------------------------------------------
    def stop_service(self, name: str) -> Dict[str, Any]:
        if name not in self.services or name not in self.active_sockets:
            return {
                "service_id": f"NET-{uuid.uuid4().hex[:10].upper()}",
                "status": "not_running",
                "timestamp": time.time()
            }

        sock = self.active_sockets[name]

        try:
            if hasattr(sock, "close"):
                sock.close()
        except:
            pass

        del self.active_sockets[name]
        self.services[name]["active"] = False

        return {
            "service_id": f"NET-{uuid.uuid4().hex[:10].upper()}",
            "status": "stopped",
            "service": name,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  NETWORK SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"NWS-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "routes": self.routes,
            "services": self.services,
            "active_sockets": list(self.active_sockets.keys())
        }

#===============================================================================
#  END OF FILE — networking_engine.py
#===============================================================================
