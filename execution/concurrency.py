import threading
import time
from queue import PriorityQueue
from concurrent.futures import ThreadPoolExecutor, Future
import uuid
import psutil
import os

from ardhanarishvara.execution.loop_protection import LoopProtection
from ardhanarishvara.execution.circuit_breaker import CircuitBreaker
from ardhanarishvara.execution.observer import observer


# ---------------------------------------------------------
# Utility: Generate Unique Job IDs
# ---------------------------------------------------------
def generate_job_id():
    return str(uuid.uuid4())


# ---------------------------------------------------------
# VRAM Locking System
# ---------------------------------------------------------
class VRAMLock:
    def __init__(self, max_vram_usage_ratio=0.90):
        self.lock = threading.Lock()
        self.max_ratio = max_vram_usage_ratio

    def _get_gpu_memory_usage(self):
        try:
            import torch
            if torch.cuda.is_available():
                used = torch.cuda.memory_allocated()
                total = torch.cuda.get_device_properties(0).total_memory
                return used / total
        except Exception:
            pass
        return 0.0

    def acquire(self):
        while True:
            usage = self._get_gpu_memory_usage()
            if usage < self.max_ratio:
                self.lock.acquire()
                return
            time.sleep(0.01)

    def release(self):
        self.lock.release()


# ---------------------------------------------------------
# Inference Job Object
# ---------------------------------------------------------
class InferenceJob:
    def __init__(self, model, inputs, priority=1, timeout=10, callback=None):
        self.model = model
        self.inputs = inputs
        self.priority = priority
        self.timeout = timeout
        self.callback = callback
        self.id = generate_job_id()


# ---------------------------------------------------------
# Safety Hooks (Timeout + Loop Protection + Circuit Breaker)
# ---------------------------------------------------------
class ConcurrencySafety:
    loop_engine = LoopProtection(max_repeats=3, ttl_seconds=5)
    breaker = CircuitBreaker(max_failures=3, ttl_seconds=10, cooldown_seconds=5)

    @staticmethod
    def enforce_timeout(job: InferenceJob, start_time):
        if time.time() - start_time > job.timeout:
            ConcurrencySafety.breaker.record_failure()
            observer.emit("timeout", {"job_id": job.id})
            raise TimeoutError(f"Inference job {job.id} exceeded timeout {job.timeout}s")

    @staticmethod
    def enforce_loop_protection(job: InferenceJob):
        if ConcurrencySafety.loop_engine.check(job.model, job.inputs):
            ConcurrencySafety.breaker.record_failure()
            ConcurrencySafety.loop_engine.quarantine(job.id)
            observer.emit("loop_detected", {"job_id": job.id})
            raise RuntimeError(f"Loop detected in job {job.id}")

    @staticmethod
    def enforce_circuit_breaker(job: InferenceJob):
        if not ConcurrencySafety.breaker.allow():
            observer.emit("circuit_block", {"job_id": job.id})
            raise RuntimeError(f"Circuit breaker active — job {job.id} blocked")


# ---------------------------------------------------------
# Inference Pool
# ---------------------------------------------------------
class InferencePool:
    def __init__(self, max_workers=8):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs = PriorityQueue()

    def submit_job(self, job: InferenceJob):
        self.jobs.put((job.priority, job))
        observer.emit("job_submitted", {"job_id": job.id})


# ---------------------------------------------------------
# Concurrency Manager
# ---------------------------------------------------------
class ConcurrencyManager:
    def __init__(self, pool: InferencePool, vram_lock: VRAMLock):
        self.pool = pool
        self.vram_lock = vram_lock

    def submit(self, job: InferenceJob):
        self.pool.submit_job(job)
        return job.id

    def run_next(self) -> Future:
        _, job = self.pool.jobs.get()
        observer.emit("job_started", {"job_id": job.id})

        def task():
            start_time = time.time()

            # Circuit Breaker Check
            ConcurrencySafety.enforce_circuit_breaker(job)

            # Loop Protection
            ConcurrencySafety.enforce_loop_protection(job)

            try:
                self.vram_lock.acquire()

                result = job.model(job.inputs)

                ConcurrencySafety.enforce_timeout(job, start_time)

                observer.emit("job_completed", {"job_id": job.id})

                if job.callback:
                    job.callback(result)

                return result

            except Exception as e:
                observer.emit("job_failed", {"job_id": job.id, "error": str(e)})
                ConcurrencySafety.breaker.record_failure()
                raise

            finally:
                self.vram_lock.release()

        return self.pool.executor.submit(task)


# ---------------------------------------------------------
# Ultra-Fast IPC Placeholder
# ---------------------------------------------------------
class UltraFastIPC:
    @staticmethod
    def send(message):
        pass

    @staticmethod
    def receive():
        return None
