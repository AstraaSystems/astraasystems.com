#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Storage Engine v6 — Local Reconstruction Codes (LRC)
#  File: storage_engine_v6_lrc.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, List, Optional

#===============================================================================
#  GF(256) FIELD (same as v5)
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
#  LRC ENCODER
#===============================================================================

class LRCEncoder:
    """
    Implements Local Reconstruction Codes:
      - Data divided into groups
      - Each group has a local parity
      - Global parity protects all groups
    """

    def __init__(self, data_shards: int, local_groups: int, global_parity: int):
        self.k = data_shards
        self.g = local_groups
        self.m = global_parity

        if self.k % self.g != 0:
            raise ValueError("Data shards must divide evenly into local groups")

        self.group_size = self.k // self.g

    #---------------------------------------------------------------------------
    #  ENCODE
    #---------------------------------------------------------------------------
    def encode(self, data: List[int]) -> Dict[str, List[int]]:
        groups = []
        local_parity = []
        global_parity = [0] * self.m

        # Split into groups
        for i in range(self.g):
            start = i * self.group_size
            end = start + self.group_size
            grp = data[start:end]
            groups.append(grp)

            # Local parity = XOR of group
            lp = 0
            for b in grp:
                lp ^= b
            local_parity.append(lp)

        # Global parity = XOR of all data
        for b in data:
            global_parity[0] ^= b

        return {
            "groups": groups,
            "local_parity": local_parity,
            "global_parity": global_parity
        }

    #---------------------------------------------------------------------------
    #  RECONSTRUCT MISSING SHARD
    #---------------------------------------------------------------------------
    def reconstruct(self, encoded: Dict[str, List[int]], missing_index: int) -> int:
        group_id = missing_index // self.group_size
        pos = missing_index % self.group_size

        group = encoded["groups"][group_id]
        lp = encoded["local_parity"][group_id]

        # If only one missing in group → local repair
        if group[pos] is None:
            val = lp
            for i, b in enumerate(group):
                if i != pos and b is not None:
                    val ^= b
            return val

        # Otherwise use global parity
        gp = encoded["global_parity"][0]
        for g in encoded["groups"]:
            for b in g:
                if b is not None:
                    gp ^= b
        return gp

#===============================================================================
#  STORAGE ENGINE V6
#===============================================================================

class StorageEngineV6LRC:
    """
    Distributed LRC storage engine.
    """

    def __init__(self, distributed_node_engine=None, k=6, g=2, m=1):
        self.encoder = LRCEncoder(k, g, m)
        self.k = k
        self.g = g
        self.m = m
        self.node_engine = distributed_node_engine

        self.volumes: Dict[str, Dict[str, Any]] = {}
        self.shard_map: Dict[str, Dict[str, str]] = {}
        self.snapshots: Dict[str, Dict[str, Any]] = {}

        self.telemetry = {
            "writes": 0,
            "reads": 0,
            "repairs": 0,
            "shards_created": 0,
            "snapshot_created": 0,
            "snapshot_restored": 0,
            "errors": 0
        }

    #---------------------------------------------------------------------------
    #  CREATE VOLUME
    #---------------------------------------------------------------------------
    def create_volume(self, name: str, size_mb: int, nodes: List[str]) -> Dict[str, Any]:
        required = self.k + self.g + self.m
        if len(nodes) < required:
            raise ValueError("Not enough nodes for LRC(K,G,M)")

        vid = f"LRCVOL-{uuid.uuid4().hex[:10].upper()}"
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
    #  WRITE (ENCODE + DISTRIBUTE)
    #---------------------------------------------------------------------------
    async def write(self, volume_id: str, data: bytes) -> Dict[str, Any]:
        if volume_id not in self.volumes:
            self.telemetry["errors"] += 1
            return {"status": "unknown_volume"}

        symbols = list(data)
        encoded = self.encoder.encode(symbols)

        shards = []
        for grp in encoded["groups"]:
            shards.extend(grp)
        shards.extend(encoded["local_parity"])
        shards.extend(encoded["global_parity"])

        shard_ids = []
        nodes = self.volumes[volume_id]["nodes"]

        for i, shard in enumerate(shards):
            sid = f"SHR-{uuid.uuid4().hex[:10].upper()}"
            node = nodes[i % len(nodes)]
            shard_ids.append(sid)
            self.shard_map[volume_id][sid] = node

            if self.node_engine:
                await self.node_engine.send(node, "storage_shard_write", {
                    "shard_id": sid,
                    "data": bytes([shard])
                })

            self.telemetry["shards_created"] += 1

        self.telemetry["writes"] += 1

        return {"status": "written", "shards": shard_ids}

    #---------------------------------------------------------------------------
    #  READ (LOCAL REPAIR FIRST)
    #---------------------------------------------------------------------------
    async def read(self, volume_id: str, shard_ids: List[str]) -> Dict[str, Any]:
        if volume_id not in self.volumes:
            self.telemetry["errors"] += 1
            return {"status": "unknown_volume"}

        shards = []
        missing = []

        for sid in shard_ids:
            node = self.shard_map[volume_id].get(sid)
            if not node:
                missing.append(sid)
                shards.append(None)
                continue

            if self.node_engine:
                res = await self.node_engine.send(node, "storage_shard_read", {
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

        if len(missing) > self.m + self.g:
            self.telemetry["errors"] += 1
            return {"status": "unrecoverable"}

        # Reconstruct missing shards
        encoded = {
            "groups": [],
            "local_parity": [],
            "global_parity": []
        }

        total = self.k + self.g + self.m
        groups = []
        idx = 0

        for _ in range(self.g):
            grp = shards[idx:idx + self.encoder.group_size]
            groups.append(grp)
            idx += self.encoder.group_size

        encoded["groups"] = groups
        encoded["local_parity"] = shards[self.k:self.k + self.g]
        encoded["global_parity"] = shards[self.k + self.g:]

        # Repair each missing shard
        for i, s in enumerate(shards):
            if s is None:
                repaired = self.encoder.reconstruct(encoded, i)
                shards[i] = repaired
                self.telemetry["repairs"] += 1

        self.telemetry["reads"] += 1

        return {"status": "ok", "data": bytes(shards[:self.k])}

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self, volume_id: str) -> Dict[str, Any]:
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
    def restore(self, snapshot_id: str) -> Dict[str, Any]:
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
    def engine_snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"LRCSTO-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "volumes": list(self.volumes.keys()),
            "snapshots": list(self.snapshots.keys()),
            "shard_map": self.shard_map,
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — storage_engine_v6_lrc.py
#===============================================================================
