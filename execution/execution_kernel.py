import time
import threading
import uuid
from concurrent.futures import Future

from ardhanarishvara.execution.concurrency import (
    InferenceJob,
    InferencePool,
    ConcurrencyManager,
    VRAMLock
)

from ardhanarishvara.execution.observer import observer


# =========================================================
# Utility: Generate Task IDs
# =========================================================

def generate_task_id():
    return str(uuid.uuid4())


# =========================================================
# Retry Policy
# =========================================================

class RetryPolicy:
    """
    Retry policy with:
    - max retries
    - backoff
    - retryable exceptions
    """

    def __init__(self, max_retries=3, backoff_seconds=1, retry_exceptions=(Exception,)):
        self.max_retries = max_retries
        self.backoff = backoff_seconds
        self.retry_exceptions = retry_exceptions


# =========================================================
# Escalation Policy
# =========================================================

class EscalationPolicy:
    """
    Escalation policy with:
    - escalation callback
    - escalation threshold
    """

    def __init__(self, threshold=3, callback=None):
        self.threshold = threshold
        self.callback = callback


# =========================================================
# Workflow Step
# =========================================================

class WorkflowStep:
    """
    Represents a single step in a workflow.
    """

    def __init__(self, model, inputs, callback=None):
        self.model = model
        self.inputs = inputs
        self.callback = callback


# =========================================================
# Workflow Engine
# =========================================================

class WorkflowEngine:
    """
    Executes multi-step workflows using the Execution Kernel.
    """

    def __init__(self, kernel):
        self.kernel = kernel

    def run(self, steps):
        results = []
        for step in steps:
            result = self.kernel.run_task(step.model, step.inputs, step.callback)
            results.append(result)
        return results


# =========================================================
# Execution Kernel
# =========================================================

class ExecutionKernel:
    """
    The heart of ARUHAN Labs:
    - task execution
    - workflow orchestration
    - retries
    - escalation
    - safety integration
    - observer events
    """

    def __init__(self):
        self.pool = InferencePool(max_workers=8)
        self.vram_lock = VRAMLock()
        self.manager = ConcurrencyManager(self.pool, self.vram_lock)

        self.retry_policy = RetryPolicy()
        self.escalation_policy = EscalationPolicy()

    # -----------------------------------------------------
    # Run a single task
    # -----------------------------------------------------
    def run_task(self, model, inputs, callback=None):
        task_id = generate_task_id()
        observer.emit("task_started", {"task_id": task_id})

        retries = 0

        while True:
            try:
                job = InferenceJob(model, inputs, callback=callback)
                future: Future = self.manager.run_next()

                result = future.result()
                observer.emit("task_completed", {"task_id": task_id})
                return result

            except self.retry_policy.retry_exceptions as e:
                retries += 1
                observer.emit("task_retry", {"task_id": task_id, "retry": retries, "error": str(e)})

                if retries > self.retry_policy.max_retries:
                    observer.emit("task_failed", {"task_id": task_id, "error": str(e)})
                    self._escalate(task_id, e)
                    raise

                time.sleep(self.retry_policy.backoff)

    # -----------------------------------------------------
    # Escalation Logic
    # -----------------------------------------------------
    def _escalate(self, task_id, error):
        observer.emit("task_escalated", {"task_id": task_id, "error": str(error)})

        if self.escalation_policy.callback:
            try:
                self.escalation_policy.callback(task_id, error)
            except Exception:
                pass

    # -----------------------------------------------------
    # Run a workflow
    # -----------------------------------------------------
    def run_workflow(self, steps):
        engine = WorkflowEngine(self)
        return engine.run(steps)
