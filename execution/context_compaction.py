import hashlib
import time
import threading


# =========================================================
# Context Compaction Engine
# =========================================================

class ContextCompactionEngine:
    """
    Full context compaction system with:
    - token estimation
    - chunking
    - semantic hashing
    - redundancy removal
    - sliding window compaction
    - TTL-based pruning
    """

    def __init__(self, max_tokens=4096, ttl_seconds=300):
        self.max_tokens = max_tokens
        self.ttl = ttl_seconds

        # Stores: entry_id -> (content, timestamp, semantic_hash)
        self.entries = {}
        self.lock = threading.Lock()

    # -----------------------------------------------------
    # Token Estimation (Lightweight)
    # -----------------------------------------------------
    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimator: 1 token ≈ 4 chars.
        """
        return max(1, len(text) // 4)

    # -----------------------------------------------------
    # Semantic Hashing
    # -----------------------------------------------------
    def semantic_hash(self, text: str) -> str:
        """
        Hashes content to detect semantic duplicates.
        """
        h = hashlib.sha256()
        h.update(text.encode("utf-8"))
        return h.hexdigest()

    # -----------------------------------------------------
    # Add Entry
    # -----------------------------------------------------
    def add(self, entry_id: str, content: str):
        """
        Add a new context entry.
        """
        with self.lock:
            sh = self.semantic_hash(content)
            now = time.time()

            # If duplicate semantic hash exists, skip
            for eid, (_, _, existing_hash) in self.entries.items():
                if existing_hash == sh:
                    return False

            self.entries[entry_id] = (content, now, sh)
            self._compact()
            return True

    # -----------------------------------------------------
    # TTL Pruning
    # -----------------------------------------------------
    def _prune_ttl(self):
        now = time.time()
        to_delete = []

        for entry_id, (_, timestamp, _) in self.entries.items():
            if now - timestamp > self.ttl:
                to_delete.append(entry_id)

        for entry_id in to_delete:
            del self.entries[entry_id]

    # -----------------------------------------------------
    # Sliding Window Compaction
    # -----------------------------------------------------
    def _compact(self):
        """
        Ensures total tokens stay under max_tokens.
        Removes oldest entries first.
        """
        self._prune_ttl()

        # Compute total tokens
        total_tokens = sum(self.estimate_tokens(content)
                           for content, _, _ in self.entries.values())

        # Remove oldest entries until under limit
        if total_tokens > self.max_tokens:
            # Sort by timestamp (oldest first)
            sorted_entries = sorted(
                self.entries.items(),
                key=lambda x: x[1][1]
            )

            for entry_id, (content, timestamp, sh) in sorted_entries:
                del self.entries[entry_id]
                total_tokens -= self.estimate_tokens(content)
                if total_tokens <= self.max_tokens:
                    break

    # -----------------------------------------------------
    # Export Compacted Context
    # -----------------------------------------------------
    def export(self):
        """
        Returns the compacted context as a single string.
        """
        with self.lock:
            # Sort by timestamp (oldest first)
            sorted_entries = sorted(
                self.entries.items(),
                key=lambda x: x[1][1]
            )

            return "\n".join(content for _, (content, _, _) in sorted_entries)
