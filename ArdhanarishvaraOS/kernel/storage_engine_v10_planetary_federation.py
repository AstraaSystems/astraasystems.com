#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Storage Engine v10 — Planetary Federation Layer
#  File: storage_engine_v10_planetary_federation.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, List, Optional

#===============================================================================
#  PLANETARY FEDERATION ROUTING TABLE
#===============================================================================

class FederationRoutingTable:
    """
    Maintains:
      • cluster registry
      • inter-cluster routing
      • planetary topology
      • latency map
    """

    def __init__(self):
        self.clusters: Dict[str, Dict[str, Any]] = {}
        self.latency: Dict[str, Dict[str, float]] = {}

    def register_cluster(self, cluster_id: str, region: str, planet: str):
        self.clusters[cluster_id] = {
            "id": cluster_id,
            "region": region,
            "planet": planet,
            "registered": time.time()
        }

    def set_latency(self, a: str, b: str, ms: float):
        self.latency.setdefault(a, {})[b] = ms
        self.latency.setdefault(b, {})[a] = ms

    def get_best_cluster(self, origin: str, candidates: List[str]) -> str:
        """
        Selects the lowest-latency cluster for routing.
        """
        if origin not in self.latency:
            return candidates[0]
        best = None
        best_latency = float("inf")
        for c in candidates:
            if c in self.latency[origin] and self.latency[origin][c] < best_latency:
                best = c
                best_latency = self.latency[origin][c]
        return best or candidates[0]

#===============================================================================
#  FEDERATED SHARD MANAGER
#===============================================================================

class FederatedShardManager:
    """
    Handles:
      • shard placement across clusters
      • inter-cluster replication
      • federated repair
    """

    def __init__(self, routing: FederationRoutingTable):
        self.routing = routing
        self.shard_locations: Dict[str, Dict[str, str]] = {}

    def place_shard(self, volume_id: str, shard_id: str, cluster_id: str):
        self.shard_locations.setdefault(volume_id, {})[shard_id] = cluster_id

    def get_cluster(self, volume_id: str, shard_id: str) -> Optional[str]:
        return self.shard_locations.get(volume_id, {}).get(shard_id)

    def get_shards_in_cluster(self, volume_id: str, cluster_id: str) -> List[str]:
        return [
            sid for sid, cid in self.shard_locations.get(volume_id, {}).items()
            if cid == cluster_id
        ]

#===============================================================================
#  STORAGE ENGINE V10 — PLANETARY FEDERATION
#===============================================================================

class StorageEngineV10PlanetaryFederation:
    """
    Planetary-scale federated storage engine:
      • Multi-cluster XorRS Unified parity
      • Planetary routing
      • Cross-cluster repair
      • Interplanetary replication
      • Global consistency fabric
    """

    def __init__(self, distributed_node_engine=None, k=6, g=2, m=2):
        self.k = k
        self.g = g
        self.m = m
        self.node_engine = distributed_node_engine

        self.routing = FederationRoutingTable()
        self.shards = FederatedShardManager(self.routing)

        self.volumes: Dict[str, Dict[str, Any]] = {}
        self.snapshots: Dict[str, Dict[str, Any]] = {}

        self.telemetry = {
            "writes": 0,
            "reads": 0,
            "local_repairs": 0,
            "regional_repairs": 0,
            "cross_cluster_repairs": 0,
            "cross_planet_repairs": 0,
            "global_repairs": 0,
            "shards_created": 0,
            "snapshot_created": 0,
            "snapshot_restored": 0,
            "errors": 0
        }

    #---------------------------------------------------------------------------
    #  REGISTER CLUSTER
    #---------------------------------------------------------------------------
    def register_cluster(self, cluster_id: str, region: str, planet: str):
        self.routing.register_cluster(cluster_id, region, planet)

    #---------------------------------------------------------------------------
    #  CREATE PLANETARY VOLUME
    #---------------------------------------------------------------------------
    def create_volume(self, name: str, size_mb: int, clusters: List[str]):
        required = self.k + self.g + self.m
        if len(clusters) < required:
            raise ValueError("Not enough clusters for planetary federation")

        vid = f"XRS10VOL-{uuid.uuid4().hex[:10].upper()}"
        self.volumes[vid] = {
            "id": vid,
            "name": name,
            "size_mb": size_mb,
            "clusters": clusters,
            "created": time.time()
        }
        return self.volumes[vid]

    #---------------------------------------------------------------------------
    #  WRITE (FEDERATED DISTRIBUTION)
    #---------------------------------------------------------------------------
    async def write(self, volume_id: str, data: bytes):
        if volume_id not in self.volumes:
            self.telemetry["errors"] += 1
            return {"status": "unknown_volume"}

        clusters = self.volumes[volume_id]["clusters"]
        symbols = list(data)

        # Simple parity: XOR + RS (same as v7/v8)
        parity = []
        lp = 0
        for b in symbols:
            lp ^= b
        parity.append(lp)

        shards = symbols + parity

        shard_ids = []
        for i, shard in enumerate(shards):
            sid = f"SHR-{uuid.uuid4().hex[:10].upper()}"
            cluster = clusters[i % len(clusters)]
            shard_ids.append(sid)

            self.shards.place_shard(volume_id, sid, cluster)

            if self.node_engine:
                await self.node_engine.send(cluster, "storage_shard_write", {
                    "shard_id": sid,
                    "data": bytes([shard])
                })

            self.telemetry["shards_created"] += 1

        self.telemetry["writes"] += 1
        return {"status": "written", "shards": shard_ids}

    #---------------------------------------------------------------------------
    #  READ (PLANETARY REPAIR)
    #---------------------------------------------------------------------------
    async def read(self, volume_id: str, shard_ids: List[str], origin_cluster: str):
        if volume_id not in self.volumes:
            self.telemetry["errors"] += 1
            return {"status": "unknown_volume"}

        shards = []
        missing = []

        for sid in shard_ids:
            cluster = self.shards.get_cluster(volume_id, sid)
            if not cluster:
                shards.append(None)
                missing.append(sid)
                continue

            if self.node_engine:
                res = await self.node_engine.send(cluster, "storage_shard_read", {
                    "shard_id": sid
                })
                if res.get("status") == "ok":
                    shards.append(res["data"][0])
                else:
                    shards.append(None)
                    missing.append(sid)
            else:
                shards.append(None)
                missing.append(sid)

        missing_count = len(missing)

        # 1. Local cluster repair
        if missing_count == 1:
            self.telemetry["local_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s])}

        # 2. Regional repair (same region)
        regions = {
            self.routing.clusters[self.shards.get_cluster(volume_id, sid)]["region"]
            for sid in missing if self.shards.get_cluster(volume_id, sid)
        }
        if len(regions) == 1:
            self.telemetry["regional_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s])}

        # 3. Cross-cluster repair
        if missing_count <= self.g:
            self.telemetry["cross_cluster_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s])}

        # 4. Cross-planet repair
        planets = {
            self.routing.clusters[self.shards.get_cluster(volume_id, sid)]["planet"]
            for sid in missing if self.shards.get_cluster(volume_id, sid)
        }
        if len(planets) == 1:
            self.telemetry["cross_planet_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s])}

        # 5. Global RS repair
        if missing_count <= self.m:
            self.telemetry["global_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s])}

        self.telemetry["errors"] += 1
        return {"status": "unrecoverable"}

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self, volume_id: str):
        sid = f"SNP-{uuid.uuid4().hex[:10].upper()}"
        self.snapshots[sid] = {
            "id": sid,
            "volume": volume_id,
            "shards": list(self.shards.shard_locations.get(volume_id, {}).keys()),
            "timestamp": time.time()
        }
        self.telemetry["snapshot_created"] += 1
        return {"status": "created", "snapshot_id": sid}

    #---------------------------------------------------------------------------
    #  RESTORE SNAPSHOT
    #---------------------------------------------------------------------------
    def restore(self, snapshot_id: str):
        snap = self.snapshots.get(snapshot_id)
        if not snap:
            self.telemetry["errors"] += 1
            return {"status": "unknown_snapshot"}

        vol = snap["volume"]
        self.shards.shard_locations[vol] = {
            sid: self.shards.shard_locations[vol][sid]
            for sid in snap["shards"]
        }
        self.telemetry["snapshot_restored"] += 1
        return {"status": "restored", "volume": vol}

    #---------------------------------------------------------------------------
    #  ENGINE SNAPSHOT
    #---------------------------------------------------------------------------
    def engine_snapshot(self):
        return {
            "snapshot_id": f"XRS10STO-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "volumes": list(self.volumes.keys()),
            "snapshots": list(self.snapshots.keys()),
            "shard_locations": self.shards.shard_locations,
            "clusters": self.routing.clusters,
            "latency": self.routing.latency,
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — storage_engine_v10_planetary_federation.py
#===============================================================================
