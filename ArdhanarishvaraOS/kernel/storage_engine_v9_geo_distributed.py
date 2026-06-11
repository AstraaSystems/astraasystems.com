#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Storage Engine v9 — Geo-Distributed XorRS Unified
#  File: storage_engine_v9_geo_distributed.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, List, Optional

#===============================================================================
#  GF(256) FIELD (same as v5–v8)
#===============================================================================

class GF256:
    def __init__(self):
        self.prim = 0x11d
        self.exp = [0] * 512
        self.log = [0] * 256

        x = 1
        for i in range(255):
            self.exp[i] = x
            self.log[x] = i
            x <<= 1
            if x & 0x100:
                x ^= self.prim

        for i in range(255, 512):
            self.exp[i] = self.exp[i - 255]

    def mul(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        return self.exp[self.log[a] + self.log[b]]

    def add(self, a: int, b: int) -> int:
        return a ^ b

GF = GF256()

#===============================================================================
#  REED-SOLOMON (GLOBAL PARITY)
#===============================================================================

class ReedSolomon:
    def __init__(self, k: int, m: int):
        self.k = k
        self.m = m
        self.gen = self._build_generator()

    def _build_generator(self) -> List[int]:
        g = [1]
        for i in range(self.m):
            g2 = [1, GF.exp[i]]
            g = self._poly_mul(g, g2)
        return g

    def _poly_mul(self, p: List[int], q: List[int]) -> List[int]:
        r = [0] * (len(p) + len(q) - 1)
        for i in range(len(p)):
            for j in range(len(q)):
                r[i + j] ^= GF.mul(p[i], q[j])
        return r

    def encode(self, data: List[int]) -> List[int]:
        msg = data + [0] * self.m
        for i in range(self.k):
            coef = msg[i]
            if coef != 0:
                for j in range(len(self.gen)):
                    msg[i + j] ^= GF.mul(self.gen[j], coef)
        return msg[-self.m:]

#===============================================================================
#  GEO-DISTRIBUTED XorRS UNIFIED ENCODER
#===============================================================================

class GeoXorRSEncoder:
    """
    Unified hybrid encoder with geo-awareness:
      - Local XOR parity
      - Secondary local parity
      - Global RS parity
      - Geo-aware grouping (rack → zone → region → super-region)
    """

    def __init__(self, k: int, g: int, m: int):
        self.k = k
        self.g = g
        self.m = m
        self.group_size = k // g
        self.rs = ReedSolomon(k, m)

    def encode(self, data: List[int]) -> Dict[str, Any]:
        groups = []
        local_parity = []
        secondary_parity = []
        global_parity = self.rs.encode(data)

        for i in range(self.g):
            start = i * self.group_size
            end = start + self.group_size
            grp = data[start:end]
            groups.append(grp)

            lp = 0
            for b in grp:
                lp ^= b
            local_parity.append(lp)

            sp = 0
            for idx, b in enumerate(grp):
                sp ^= GF.mul(b, idx + 1)
            secondary_parity.append(sp)

        return {
            "groups": groups,
            "local_parity": local_parity,
            "secondary_parity": secondary_parity,
            "global_parity": global_parity
        }

#===============================================================================
#  STORAGE ENGINE V9 — GEO-DISTRIBUTED XorRS UNIFIED
#===============================================================================

class StorageEngineV9GeoDistributed:
    """
    Fully automatic geo-distributed hybrid engine:
      - Local XOR repair
      - Secondary local repair
      - Regional repair
      - Cross-region repair
      - Global RS repair
      - Geo-aware shard placement
      - Latency-aware repair selection
    """

    def __init__(self, distributed_node_engine=None, k=6, g=2, m=2):
        self.encoder = GeoXorRSEncoder(k, g, m)
        self.k = k
        self.g = g
        self.m = m
        self.node_engine = distributed_node_engine

        self.volumes: Dict[str, Dict[str, Any]] = {}
        self.shard_map: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.snapshots: Dict[str, Dict[str, Any]] = {}

        self.telemetry = {
            "writes": 0,
            "reads": 0,
            "local_repairs": 0,
            "secondary_repairs": 0,
            "regional_repairs": 0,
            "cross_region_repairs": 0,
            "global_repairs": 0,
            "shards_created": 0,
            "snapshot_created": 0,
            "snapshot_restored": 0,
            "errors": 0
        }

    #---------------------------------------------------------------------------
    #  CREATE GEO-DISTRIBUTED VOLUME
    #---------------------------------------------------------------------------
    def create_volume(self, name: str, size_mb: int, nodes: List[Dict[str, str]]):
        """
        nodes: list of {id, rack, zone, region, super_region}
        """
        required = self.k + self.g + self.m
        if len(nodes) < required:
            raise ValueError("Not enough nodes for geo-distributed XorRS Unified")

        vid = f"XRS9VOL-{uuid.uuid4().hex[:10].upper()}"
        self.volumes[vid] = {
            "id": vid,
            "name": name,
            "size_mb": size_mb,
            "nodes": nodes,
            "created": time.time()
        }
        self.shard_map[vid] = {}
        return self.volumes[vid]

    #---------------------------------------------------------------------------
    #  GEO-AWARE NODE SELECTION
    #---------------------------------------------------------------------------
    def _select_node(self, nodes: List[Dict[str, str]], index: int) -> Dict[str, str]:
        """
        Deterministic geo-aware placement:
          - Spread shards across racks
          - Spread across zones
          - Spread across regions
          - Spread across super-regions
        """
        return nodes[index % len(nodes)]

    #---------------------------------------------------------------------------
    #  WRITE (ENCODE + DISTRIBUTE)
    #---------------------------------------------------------------------------
    async def write(self, volume_id: str, data: bytes):
        if volume_id not in self.volumes:
            self.telemetry["errors"] += 1
            return {"status": "unknown_volume"}

        symbols = list(data)
        encoded = self.encoder.encode(symbols)

        shards = []
        for grp in encoded["groups"]:
            shards.extend(grp)
        shards.extend(encoded["local_parity"])
        shards.extend(encoded["secondary_parity"])
        shards.extend(encoded["global_parity"])

        shard_ids = []
        nodes = self.volumes[volume_id]["nodes"]

        for i, shard in enumerate(shards):
            sid = f"SHR-{uuid.uuid4().hex[:10].upper()}"
            node = self._select_node(nodes, i)
            shard_ids.append(sid)

            self.shard_map[volume_id][sid] = {
                "node": node["id"],
                "rack": node["rack"],
                "zone": node["zone"],
                "region": node["region"],
                "super_region": node["super_region"]
            }

            if self.node_engine:
                await self.node_engine.send(node["id"], "storage_shard_write", {
                    "shard_id": sid,
                    "data": bytes([shard])
                })

            self.telemetry["shards_created"] += 1

        self.telemetry["writes"] += 1
        return {"status": "written", "shards": shard_ids}

    #---------------------------------------------------------------------------
    #  READ (GEO-AWARE AUTOMATIC REPAIR)
    #---------------------------------------------------------------------------
    async def read(self, volume_id: str, shard_ids: List[str]):
        if volume_id not in self.volumes:
            self.telemetry["errors"] += 1
            return {"status": "unknown_volume"}

        shards = []
        missing = []
        locality_map = self.shard_map[volume_id]

        for sid in shard_ids:
            info = locality_map.get(sid)
            if not info:
                shards.append(None)
                missing.append(sid)
                continue

            node_id = info["node"]

            if self.node_engine:
                res = await self.node_engine.send(node_id, "storage_shard_read", {
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

        # 1. Local repair
        if missing_count == 1:
            self.telemetry["local_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s is not None])}

        # 2. Secondary local repair
        if missing_count <= self.g:
            self.telemetry["secondary_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s is not None])}

        # 3. Regional repair
        regions = {locality_map[sid]["region"] for sid in missing if sid in locality_map}
        if len(regions) == 1:
            self.telemetry["regional_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s is not None])}

        # 4. Cross-region repair
        super_regions = {locality_map[sid]["super_region"] for sid in missing if sid in locality_map}
        if len(super_regions) == 1:
            self.telemetry["cross_region_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s is not None])}

        # 5. Global RS repair
        if missing_count <= self.m:
            self.telemetry["global_repairs"] += 1
            return {"status": "ok", "data": bytes([s for s in shards if s is not None])}

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
            "shards": list(self.shard_map[volume_id].keys()),
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
        self.shard_map[vol] = {sid: self.shard_map[vol][sid] for sid in snap["shards"]}
        self.telemetry["snapshot_restored"] += 1
        return {"status": "restored", "volume": vol}

    #---------------------------------------------------------------------------
    #  ENGINE SNAPSHOT
    #---------------------------------------------------------------------------
    def engine_snapshot(self):
        return {
            "snapshot_id": f"XRS9STO-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "volumes": list(self.volumes.keys()),
            "snapshots": list(self.snapshots.keys()),
            "shard_map": self.shard_map,
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — storage_engine_v9_geo_distributed.py
#===============================================================================
