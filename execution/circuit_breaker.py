import time
import threading


# =========================================================
# Circuit Breaker + TTL Engine
# =========================================================

class CircuitBreaker:
    """
    Full circuit breaker system with:
    - failure counters
    - TTL (time-to-live)
    - cooldown window
    - auto-trip
    - auto-reset
    """

    def __init__(self, max_failures=3, ttl_seconds=10, cooldown_seconds=5):
        self.max_failures = max_failures
        self.ttl = ttl_seconds
        self.cooldown = cooldown_seconds

        self.failures = 0
        self.last_failure_time = 0
        self.tripped = False
        self.lock = threading.Lock()

    def _reset_if_ttl_expired(self):
        """
        Reset failure count if TTL window has passed.
        """
        if time.time() - self.last_failure_time > self.ttl:
            self.failures = 0
            self.tripped = False

    def record_failure(self):
        """
        Record a failure and trip breaker if needed.
        """
        with self.lock:
            self._reset_if_ttl_expired()

            self.failures += 1
            self.last_failure_time = time.time()

            if self.failures >= self.max_failures:
                self.tripped = True

    def allow(self):
        """
        Check if circuit breaker allows execution.
        """
        with self.lock:
            if not self.tripped:
                return True

            # If tripped, check cooldown
            if time.time() - self.last_failure_time > self.cooldown:
                self.tripped = False
                self.failures = 0
                return True

            return False

    def trip(self):
        """
        Manually trip breaker.
        """
        with self.lock:
            self.tripped = True
            self.last_failure_time = time.time()

    def reset(self):
        """
        Manually reset breaker.
        """
        with self.lock:
            self.tripped = False
            self.failures = 0
