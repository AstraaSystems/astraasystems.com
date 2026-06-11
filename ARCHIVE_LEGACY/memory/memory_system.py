import time
import threading
import uuid
import hashlib
import math


# =========================================================
# Utility: Generate Unique Memory IDs
# =========================================================

def generate_memory_id():
    return str(uuid.uuid4())


# =========================================================
# Short-Term Memory (STM)
# =========================================================

class ShortTermMemory:
    """
    Short-term memory system with:
    - time-based expiration
    - capacity limit
    - FIFO eviction
    """

    def __init__(self, max_entries=128, ttl_seconds=300):
        self.max_entries = max_entries
        self.ttl = ttl_seconds
        self.lock = threading.Lock()

        # entry_id -> (content, timestamp)
        self.entries = {}

    def add(self, content: str):
        with self.lock:
            entry_id = generate_memory_id()
            self.entries[entry_id] = (content, time.time())
            self._evict()
            return entry_id

    def _evict(self):
        now = time.time()

        # TTL eviction
        expired = [
            eid for eid, (_, ts) in self.entries.items()
            if now - ts > self.ttl
        ]
        for eid in expired:
            del self.entries[eid]

        # Capacity eviction (FIFO)
        if len(self.entries) > self.max_entries:
            sorted_entries = sorted(self.entries.items(), key=lambda x: x[1][1])
            to_remove = len(self.entries) - self.max_entries
            for i in range(to_remove):
                del self.entries[sorted_entries[i][0]]

    def export(self):
        with self.lock:
            sorted_entries = sorted(self.entries.items(), key=lambda x: x[1][1])
            return [content for _, (content, _) in sorted_entries]


# =========================================================
# Long-Term Memory (LTM)
# =========================================================

class LongTermMemory:
    """
    Long-term memory system with:
    - persistent storage
    - timestamped entries
    - semantic hashing for deduplication
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.entries = {}  # entry_id -> (content, timestamp, semantic_hash)

    def _semantic_hash(self, text: str):
        h = hashlib.sha256()
        h.update(text.encode("utf-8"))
        return h.hexdigest()

    def add(self, content: str):
        with self.lock:
            sh = self._semantic_hash(content)

            # Deduplicate
            for eid, (_, _, existing_hash) in self.entries.items():
                if existing_hash == sh:
                    return eid

            entry_id = generate_memory_id()
            self.entries[entry_id] = (content, time.time(), sh)
            return entry_id

    def search(self, query: str):
        """
        Simple keyword search.
        """
        with self.lock:
            results = []
            for eid, (content, ts, _) in self.entries.items():
                if query.lower() in content.lower():
                    results.append((eid, content, ts))
            return results

    def export(self):
        with self.lock:
            sorted_entries = sorted(self.entries.items(), key=lambda x: x[1][1])
            return [content for _, (content, _, _) in sorted_entries]


# =========================================================
# Vector Memory (Semantic Embeddings)
# =========================================================

class VectorMemory:
    """
    Vector memory system with:
    - embedding model
    - cosine similarity search
    - vector store
    """

    def __init__(self, embedder_model):
        self.embedder = embedder_model
        self.lock = threading.Lock()

        # entry_id -> (content, vector)
        self.vectors = {}

    def _cosine(self, a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0
        return dot / (norm_a * norm_b)

    def add(self, content: str):
        with self.lock:
            vec = self.embedder(content)
            entry_id = generate_memory_id()
            self.vectors[entry_id] = (content, vec)
            return entry_id

    def search(self, query: str, top_k=5):
        with self.lock:
            qvec = self.embedder(query)
            scored = []

            for eid, (content, vec) in self.vectors.items():
                score = self._cosine(qvec, vec)
                scored.append((score, eid, content))

            scored.sort(reverse=True)
            return scored[:top_k]


# =========================================================
# Memory Bridge (Unified Interface)
# =========================================================

class MemoryBridge:
    """
    Unified memory interface combining:
    - Short-term memory
    - Long-term memory
    - Vector memory
    """

    def __init__(self, embedder_model):
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        self.vmem = VectorMemory(embedder_model)

    def add(self, content: str):
        """
        Add content to all memory systems.
        """
        stm_id = self.stm.add(content)
        ltm_id = self.ltm.add(content)
        vmem_id = self.vmem.add(content)

        return {
            "stm_id": stm_id,
            "ltm_id": ltm_id,
            "vmem_id": vmem_id
        }

    def search(self, query: str):
        """
        Unified search across all memory systems.
        """
        return {
            "stm": self.stm.export(),
            "ltm": self.ltm.search(query),
            "vmem": self.vmem.search(query)
        }

    def export_all(self):
        """
        Export all memory content.
        """
        return {
            "short_term": self.stm.export(),
            "long_term": self.ltm.export(),
            "vector_memory": [
                content for _, (content, _) in self.vmem.vectors.items()
            ]
        }
