#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Network Orchestration Engine — Topology, Routing & Discovery Core
#  File: network_orchestration_engine.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, Optional, List

class NetworkOrchestrationEngine:
    """
    Provides:
      • network topology registry
      • link state tracking
      • routing table orchestration
      • service discovery
      • adaptive path selection
      • network health telemetry
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.links: Dict[str, Dict[str, Any]] = {}
        self.services: Dict[str, List[str]] = {}
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.telemetry: Dict[str, Any] = {
            "nodes_added": 0,
            "links_added": 0,
            "routes_computed": 0,
            "services_registered": 0,
            "errors": 0
        }

    #---------------------------------------------------------------------------
    #  ADD NODE
    #---------------------------------------------------------------------------
    def add_node(self, name: str, address: str) -> Dict[str, Any]:
        nid = f"NETN-{uuid.uuid4().hex[:10].upper()}"
        self.nodes[nid] = {
            "id": nid,
            "name": name,
            "address": address,
            "timestamp": time.time()
        }
        self.telemetry["nodes_added"] += 1
        return self.nodes[nid]

    #---------------------------------------------------------------------------
    #  ADD LINK
    #---------------------------------------------------------------------------
    def add_link(self, node_a: str, node_b: str, cost: float) -> Dict[str, Any]:
        if node_a not in self.nodes or node_b not in self.nodes:
            self.telemetry["errors"] += 1
            return {
                "link_id": None,
                "status": "unknown_node",
                "timestamp": time.time()
            }

        lid = f"LNK-{uuid.uuid4().hex[:10].upper()}"
        self.links[lid] = {
            "id": lid,
            "a": node_a,
            "b": node_b,
            "cost": cost,
            "timestamp": time.time()
        }
        self.telemetry["links_added"] += 1
        return self.links[lid]

    #---------------------------------------------------------------------------
    #  REGISTER SERVICE
    #---------------------------------------------------------------------------
    def register_service(self, service: str, node_id: str):
        if node_id not in self.nodes:
            self.telemetry["errors"] += 1
            return

        if service not in self.services:
            self.services[service] = []

        if node_id not in self.services[service]:
            self.services[service].append(node_id)

        self.telemetry["services_registered"] += 1

    #---------------------------------------------------------------------------
    #  DISCOVER SERVICE
    #---------------------------------------------------------------------------
    def discover(self, service: str) -> List[str]:
        return self.services.get(service, [])

    #---------------------------------------------------------------------------
    #  COMPUTE ROUTE (DIJKSTRA-LIKE SIMPLIFIED)
    #---------------------------------------------------------------------------
    def compute_route(self, start: str, end: str) -> Dict[str, Any]:
        if start not in self.nodes or end not in self.nodes:
            self.telemetry["errors"] += 1
            return {
                "route_id": f"RTE-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_node",
                "timestamp": time.time()
            }

        # Build adjacency
        adj = {}
        for lid, link in self.links.items():
            a, b, cost = link["a"], link["b"], link["cost"]
            adj.setdefault(a, []).append((b, cost))
            adj.setdefault(b, []).append((a, cost))

        # Dijkstra-like
        dist = {n: float("inf") for n in self.nodes}
        prev = {n: None for n in self.nodes}
        dist[start] = 0
        unvisited = set(self.nodes.keys())

        while unvisited:
            current = min(unvisited, key=lambda n: dist[n])
            unvisited.remove(current)

            if current == end:
                break

            for neighbor, cost in adj.get(current, []):
                alt = dist[current] + cost
                if alt < dist[neighbor]:
                    dist[neighbor] = alt
                    prev[neighbor] = current

        # Reconstruct path
        path = []
        cur = end
        while cur:
            path.append(cur)
            cur = prev[cur]
        path.reverse()

        rid = f"RTE-{uuid.uuid4().hex[:10].upper()}"
        route = {
            "id": rid,
            "start": start,
            "end": end,
            "path": path,
            "cost": dist[end],
            "timestamp": time.time()
        }

        self.routes[rid] = route
        self.telemetry["routes_computed"] += 1
        return route

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"NETO-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "nodes": self.nodes,
            "links": self.links,
            "services": self.services,
            "routes": self.routes,
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — network_orchestration_engine.py
#===============================================================================
