import threading
import time
import uuid
import json
import socket
import requests

from ardhanarishvara.aruhan.aruhan_orchestrator import ARUHAN
from ardhanarishvara.execution.observer import observer


# =========================================================
# Utility: Generate Node IDs
# =========================================================

def generate_node_id():
    return str(uuid.uuid4())


# =========================================================
# RPC Client
# =========================================================

class RPCClient:
    """
    Simple HTTP-based RPC client for node-to-node communication.
    """

    def __init__(self, host, port):
        self.base = f"http://{host}:{port}"

    def call(self, endpoint, payload):
        try:
            res = requests.post(f"{self.base}/{endpoint}", json=payload, timeout=3)
            return res.json()
        except Exception as e:
            return {"error": str(e)}


# =========================================================
# Distributed Message Bus
# =========================================================

class DistributedMessageBus:
    """
    Cluster-wide message bus.

    Features:
    - inter-node messaging
    - broadcast
    - routing to local ARUHAN
    """

    def __init__(self, node):
        self.node = node

    def send(self, target_node_id, content):
        if target_node_id == self.node.node_id:
            return self.node.aruhan.execute(content)

        if target_node_id not in self.node.cluster.nodes:
            return {"error": "unknown_node"}

        target = self.node.cluster.nodes[target_node_id]
        client = RPCClient(target["host"], target["port"])

        return client.call("distributed/receive", {
            "sender": self.node.node_id,
            "content": content
        })

    def broadcast(self, content):
        results = {}
        for nid, info in self.node.cluster.nodes.items():
            if nid == self.node.node_id:
                continue

            client = RPCClient(info["host"], info["port"])
            results[nid] = client.call("distributed/receive", {
                "sender": self.node.node_id,
                "content": content
            })

        return results


# =========================================================
# Cluster Manager
# =========================================================

class ClusterManager:
    """
    Maintains cluster membership and node registry.
    """

    def __init__(self):
        self.nodes = {}
        self.lock = threading.Lock()

    def register(self, node_id, host, port):
        with self.lock:
            self.nodes[node_id] = {"host": host, "port": port}
            observer.emit("cluster_node_registered", {"node": node_id})

    def unregister(self, node_id):
        with self.lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
                observer.emit("cluster_node_unregistered", {"node": node_id})


# =========================================================
# Distributed Node
# =========================================================

class DistributedNode:
    """
    A single node in the distributed cluster.

    Each node contains:
    - its own ARUHAN instance
    - distributed message bus
    - RPC server (FastAPI)
    """

    def __init__(self, embedder_model, host="127.0.0.1", port=9000, cluster=None):
        self.node_id = generate_node_id()
        self.host = host
        self.port = port

        self.aruhan = ARUHAN(embedder_model)
        self.cluster = cluster or ClusterManager()
        self.bus = DistributedMessageBus(self)

        self.cluster.register(self.node_id, host, port)

        # FastAPI server
        from fastapi import FastAPI
        from pydantic import BaseModel

        self.app = FastAPI(title=f"Distributed Node {self.node_id}")

        class ReceiveRequest(BaseModel):
            sender: str
            content: str

        @self.app.post("/distributed/receive")
        def receive(req: ReceiveRequest):
            observer.emit("distributed_message_received", {
                "node": self.node_id,
                "from": req.sender,
                "content": req.content
            })
            return {"result": self.aruhan.execute(req.content)}

    def get_app(self):
        return self.app


# =========================================================
# Distributed Cluster
# =========================================================

class DistributedCluster:
    """
    High-level interface for managing a distributed cluster.

    Features:
    - create nodes
    - broadcast commands
    - route tasks to specific nodes
    - distributed ARUHAN execution
    """

    def __init__(self, embedder_model):
        self.embedder_model = embedder_model
        self.cluster = ClusterManager()
        self.nodes = {}

    # -----------------------------------------------------
    # Create Node
    # -----------------------------------------------------
    def create_node(self, host="127.0.0.1", port=None):
        if port is None:
            port = 9000 + len(self.nodes)

        node = DistributedNode(self.embedder_model, host, port, self.cluster)
        self.nodes[node.node_id] = node

        return node

    # -----------------------------------------------------
    # Send Command to Node
    # -----------------------------------------------------
    def send(self, node_id, command):
        if node_id not in self.nodes:
            return {"error": "unknown_node"}

        node = self.nodes[node_id]
        return node.aruhan.execute(command)

    # -----------------------------------------------------
    # Broadcast Command to All Nodes
    # -----------------------------------------------------
    def broadcast(self, command):
        results = {}
        for nid, node in self.nodes.items():
            results[nid] = node.aruhan.execute(command)
        return results

    # -----------------------------------------------------
    # Get Node Apps (for running servers)
    # -----------------------------------------------------
    def get_apps(self):
        return {nid: node.get_app() for nid, node in self.nodes.items()}
