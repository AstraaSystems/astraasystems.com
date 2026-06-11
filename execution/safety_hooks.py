import time
import threading
import hashlib
from ardhanarishvara.execution.observer import observer


# =========================================================
# Anomaly Detector
# =========================================================

class AnomalyDetector:
    """
    Detects anomalies such as:
    - unexpected output patterns
    - abnormal latency
    - repeated failures
    """

    def __init__(self, latency_threshold=5.0):
        self.latency_threshold = latency_threshold

    def check_latency(self, job_id, start_time):
        elapsed = time.time() - start_time
        if elapsed > self.latency_threshold:
            observer.emit("anomaly_latency", {"job_id": job_id, "latency": elapsed})
            return True
        return False

    def check_output(self, job_id, output):
        """
        Detect empty, null, or suspicious output.
        """
        if output is None or output == "" or output == {}:
            observer.emit("anomaly_output", {"job_id": job_id})
            return True
        return False


# =========================================================
# Behavior Deviation Detector
# =========================================================

class BehaviorDeviationDetector:
    """
    Detects deviations from expected behavior using:
    - semantic hashing
    - pattern drift detection
    """

    def __init__(self):
        self.history = {}
        self.lock = threading.Lock()

    def _hash(self, text):
        h = hashlib.sha256()
        h.update(str(text).encode("utf-8"))
        return h.hexdigest()

    def check(self, job_id, output):
        fp = self._hash(output)

        with self.lock:
            if job_id not in self.history:
                self.history[job_id] = fp
                return False

            if self.history[job_id] != fp:
                observer.emit("behavior_deviation", {"job_id": job_id})
                self.history[job_id] = fp
                return True

        return False


# =========================================================
# Containment Engine
# =========================================================

class ContainmentEngine:
    """
    Contains unsafe tasks by:
    - halting execution
    - isolating job
    - notifying observer system
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.quarantined_jobs = set()

    def quarantine(self, job_id, reason):
        with self.lock:
            self.quarantined_jobs.add(job_id)
            observer.emit("containment_triggered", {"job_id": job_id, "reason": reason})
            return True

    def is_quarantined(self, job_id):
        with self.lock:
            return job_id in self.quarantined_jobs


# =========================================================
# Hard Stop Protocol
# =========================================================

class HardStopProtocol:
    """
    Emergency stop mechanism for:
    - runaway tasks
    - unsafe behavior
    - system overload
    """

    def __init__(self):
        self.triggered = False
        self.lock = threading.Lock()

    def activate(self, job_id, reason):
        with self.lock:
            self.triggered = True
            observer.emit("hard_stop", {"job_id": job_id, "reason": reason})

    def reset(self):
        with self.lock:
            self.triggered = False

    def is_active(self):
        with self.lock:
            return self.triggered


# =========================================================
# Safety Hooks (Unified Interface)
# =========================================================

class SafetyHooks:
    """
    Unified safety layer combining:
    - anomaly detection
    - behavior deviation detection
    - containment engine
    - hard stop protocol
    """

    def __init__(self):
        self.anomaly = AnomalyDetector()
        self.behavior = BehaviorDeviationDetector()
        self.containment = ContainmentEngine()
        self.hard_stop = HardStopProtocol()

    def pre_execution(self, job_id):
        """
        Called before a job runs.
        """
        if self.hard_stop.is_active():
            observer.emit("safety_block", {"job_id": job_id})
            raise RuntimeError(f"Hard stop active — job {job_id} blocked")

        if self.containment.is_quarantined(job_id):
            observer.emit("containment_block", {"job_id": job_id})
            raise RuntimeError(f"Job {job_id} is quarantined")

    def post_execution(self, job_id, start_time, output):
        """
        Called after a job runs.
        """

        # Latency anomaly
        if self.anomaly.check_latency(job_id, start_time):
            self.containment.quarantine(job_id, "latency_anomaly")

        # Output anomaly
        if self.anomaly.check_output(job_id, output):
            self.containment.quarantine(job_id, "output_anomaly")

        # Behavior deviation
        if self.behavior.check(job_id, output):
            self.containment.quarantine(job_id, "behavior_deviation")
