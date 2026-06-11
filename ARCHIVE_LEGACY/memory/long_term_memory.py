"""
ARKA Long-Term Memory System
----------------------------
Provides persistent episodic and semantic memory storage for:
- ARKA Core
- Astra
- Aruhan
- Multi-agent collaboration

Storage format: JSONL (append-only, safe, durable)
"""

from typing import Dict, Any, List, Optional
from .storage.jsonl_store import JSONLStore
from .utils.timestamp import now_timestamp


class LongTermMemory:
    def __init__(self, base_path="ardhanarishvara/memory/data"):
        self.episodic_store = JSONLStore(f"{base_path}/episodic.jsonl")
        self.semantic_store = JSONLStore(f"{base_path}/semantic.jsonl")

    # -----------------------------
    # Episodic Memory
    # -----------------------------
    def store_episode(self, event: str, metadata: Optional[Dict[str, Any]] = None):
        record = {
            "type": "episode",
            "event": event,
            "metadata": metadata or {},
            "timestamp": now_timestamp()
        }
        self.episodic_store.append(record)
        return True

    def recall_episodes(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        episodes = self.episodic_store.read_all()
        if query:
            return [e for e in episodes if query.lower() in e["event"].lower()]
        return episodes

    # -----------------------------
    # Semantic Memory
    # -----------------------------
    def store_fact(self, key: str, value: Any):
        record = {
            "type": "semantic",
            "key": key,
            "value": value,
            "timestamp": now_timestamp()
        }
        self.semantic_store.append(record)
        return True

    def recall_fact(self, key: str) -> Optional[Any]:
        facts = self.semantic_store.read_all()
        for f in reversed(facts):
            if f["key"] == key:
                return f["value"]
        return None

    # -----------------------------
    # Consolidation
    # -----------------------------
    def consolidate(self):
        """
        Future expansion: compress old memories, merge duplicates.
        """
        return True

    # -----------------------------
    # Pruning
    # -----------------------------
    def prune(self, max_records: int = 5000):
        self.episodic_store.trim(max_records)
        self.semantic_store.trim(max_records)
        return True
