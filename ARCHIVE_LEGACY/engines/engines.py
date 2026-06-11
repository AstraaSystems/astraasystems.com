import threading
from ardhanarishvara.execution.execution_kernel import ExecutionKernel
from ardhanarishvara.execution.observer import observer


# =========================================================
# Base Engine
# =========================================================

class BaseEngine:
    """
    Base class for all engines.
    Provides:
    - execution kernel
    - observer integration
    - thread safety
    """

    def __init__(self, name):
        self.name = name
        self.kernel = ExecutionKernel()
        self.lock = threading.Lock()

    def _emit(self, event, payload):
        observer.emit(event, {"engine": self.name, **payload})


# =========================================================
# Task Engine (General Purpose)
# =========================================================

class TaskEngine(BaseEngine):
    """
    General-purpose engine for:
    - running tasks
    - executing functions
    - performing operations
    """

    def run(self, data):
        """
        Expected payload:
        {
            "model": callable,
            "inputs": any
        }
        """
        model = data.get("model")
        inputs = data.get("inputs")

        self._emit("engine_task_started", {"inputs": inputs})

        result = self.kernel.run_task(model, inputs)

        self._emit("engine_task_completed", {"result": result})
        return result


# =========================================================
# Reasoning Engine (Planning, Reflection, CoT)
# =========================================================

class ReasoningEngine(BaseEngine):
    """
    Engine for:
    - chain-of-thought reasoning
    - planning
    - reflection
    - multi-step logic
    """

    def reason(self, data):
        """
        Expected payload:
        {
            "steps": [
                {"model": callable, "inputs": ...},
                ...
            ]
        }
        """
        steps_data = data.get("steps", [])
        steps = []

        for step in steps_data:
            model = step.get("model")
            inputs = step.get("inputs")
            steps.append(self.kernel.run_task(model, inputs))

        final = steps[-1] if steps else None

        self._emit("engine_reasoning_completed", {"result": final})
        return final


# =========================================================
# Domain Engine (Specialized Logic)
# =========================================================

class DomainEngine(BaseEngine):
    """
    Engine for domain-specific tasks:
    - finance
    - medical
    - legal
    - science
    - engineering
    """

    def execute(self, data):
        """
        Expected payload:
        {
            "domain": "...",
            "model": callable,
            "inputs": ...
        }
        """
        domain = data.get("domain")
        model = data.get("model")
        inputs = data.get("inputs")

        self._emit("engine_domain_started", {"domain": domain})

        result = self.kernel.run_task(model, inputs)

        self._emit("engine_domain_completed", {"domain": domain, "result": result})
        return result
