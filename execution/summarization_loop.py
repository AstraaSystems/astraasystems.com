import time
import threading
from ardhanarishvara.execution.context_compaction import ContextCompactionEngine


# =========================================================
# Automated Summarization Loop
# =========================================================

class AutomatedSummarizationLoop:
    """
    Full automated summarization system with:
    - periodic summarization
    - context compaction integration
    - long-term memory consolidation
    - semantic chunking
    - thread-safe background loop
    """

    def __init__(self, summarizer_model, interval_seconds=60, max_chunk_size=2048):
        """
        summarizer_model: callable that accepts text and returns a summary
        interval_seconds: how often to run summarization
        max_chunk_size: max tokens per summarization chunk
        """
        self.summarizer = summarizer_model
        self.interval = interval_seconds
        self.max_chunk = max_chunk_size

        self.compactor = ContextCompactionEngine()
        self.running = False
        self.thread = None

        # Long-term memory store
        self.long_term_memory = []

        # Lock for thread safety
        self.lock = threading.Lock()

    # -----------------------------------------------------
    # Add raw context entry
    # -----------------------------------------------------
    def add_context(self, entry_id: str, content: str):
        """
        Add raw context to compactor.
        """
        self.compactor.add(entry_id, content)

    # -----------------------------------------------------
    # Chunking for summarization
    # -----------------------------------------------------
    def _chunk_context(self, text: str):
        """
        Break context into manageable chunks for summarization.
        """
        words = text.split()
        chunks = []
        current = []

        for word in words:
            current.append(word)
            if len(current) >= self.max_chunk:
                chunks.append(" ".join(current))
                current = []

        if current:
            chunks.append(" ".join(current))

        return chunks

    # -----------------------------------------------------
    # Summarization Pass
    # -----------------------------------------------------
    def _summarize_context(self):
        """
        Summarize compacted context and store in long-term memory.
        """
        with self.lock:
            compacted = self.compactor.export()

            if not compacted.strip():
                return

            chunks = self._chunk_context(compacted)
            summaries = []

            for chunk in chunks:
                try:
                    summary = self.summarizer(chunk)
                    summaries.append(summary)
                except Exception:
                    continue

            # Merge summaries into a single consolidated summary
            final_summary = "\n".join(summaries)

            # Store in long-term memory
            self.long_term_memory.append({
                "timestamp": time.time(),
                "summary": final_summary
            })

            # Clear compactor after summarization
            self.compactor.entries.clear()

    # -----------------------------------------------------
    # Background Loop
    # -----------------------------------------------------
    def _loop(self):
        while self.running:
            try:
                self._summarize_context()
            except Exception:
                pass

            time.sleep(self.interval)

    # -----------------------------------------------------
    # Start Loop
    # -----------------------------------------------------
    def start(self):
        """
        Start automated summarization loop.
        """
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    # -----------------------------------------------------
    # Stop Loop
    # -----------------------------------------------------
    def stop(self):
        """
        Stop automated summarization loop.
        """
        self.running = False
        if self.thread:
            self.thread.join()

    # -----------------------------------------------------
    # Export Long-Term Memory
    # -----------------------------------------------------
    def export_long_term_memory(self):
        """
        Return all stored summaries.
        """
        with self.lock:
            return list(self.long_term_memory)
