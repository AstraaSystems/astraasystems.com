import hashlib
import time
import threading


# =========================================================
# Loop Protection Engine
# =========================================================

class LoopProtection:
    """
    Full loop protection system with:
    - execution fingerprinting
    - recurrence detection
    - loop counters
    - TTL (time-to-live)
    - quarantine mode
    """

    def __init__(self, max_repeats=3, ttl_seconds=5):
        self.max_repeats = max_repeats
        self.ttl = ttl_seconds

        # Stores: fingerprint -> (count, last_timestamp)
        self.history = {}
        self.lock = threading.Lock()

    def _fingerprint(self, model, inputs):
        """
        Create a stable fingerprint of the inference request.
        """
        h = hashlib.sha256()
        h.update(str(model).encode("utf-8"))
        h.update(str(inputs).encode("utf-8"))
        return h.hexdigest()

    def check(self, model, inputs):
        """
        Check if this inference request is looping.
        Returns:
            - False if safe
            - True if loop detected
        """
        fp = self._fingerprint(model, inputs)
        now = time.time()

        with self.lock:
            if fp not in self.history:
                self.history[fp] = [1, now]
                return False

            count, last_time = self.history[fp]

            # Reset if TTL expired
            if now - last_time > self.ttl:
                self.history[fp] = [1, now]
                return False

            # Increment loop count
            count += 1
            self.history[fp] = [count, now]

            # Loop detected
            if count > self.max_repeats:
                return True

        return False

    def quarantine(self, job_id):
        """
        Quarantine a job that triggered loop protection.
        """
        print(f"[LOOP-PROTECTION] Job {job_id} quarantined due to repeated execution pattern.")
        # Future: send to observer system or safety engine
        return True
