import threading
from ardhanarishvara.execution.execution_kernel import ExecutionKernel
from ardhanarishvara.execution.observer import observer
from ardhanarishvara.memory.memory_system import MemoryBridge


# =========================================================
# Base Sector
# =========================================================

class BaseSector:
    """
    Base class for all ASTRAA sectors.
    Provides:
    - memory bridge
    - execution kernel
    - observer integration
    - thread safety
    """

    def __init__(self, name, embedder_model):
        self.name = name
        self.kernel = ExecutionKernel()
        self.memory = MemoryBridge(embedder_model)
        self.lock = threading.Lock()

    def _emit(self, event, payload):
        observer.emit(event, {"sector": self.name, **payload})

    def _remember(self, text):
        """
        Store text in STM, LTM, and Vector Memory.
        """
        return self.memory.add(text)

    def _recall(self, query):
        """
        Unified memory search.
        """
        return self.memory.search(query)


# =========================================================
# Communication Sector
# =========================================================

class CommunicationSector(BaseSector):
    """
    Handles:
    - natural language understanding
    - conversation flow
    - summarization
    - context interpretation
    """

    def interpret(self, context):
        """
        Expected payload:
        {
            "message": "...",
            "model": callable
        }
        """
        message = context.get("message")
        model = context.get("model")

        self._remember(message)
        self._emit("sector_comm_started", {"message": message})

        result = self.kernel.run_task(model, message)

        self._emit("sector_comm_completed", {"result": result})
        return result


# =========================================================
# Analysis Sector
# =========================================================

class AnalysisSector(BaseSector):
    """
    Handles:
    - data analysis
    - pattern detection
    - summarization
    - insight extraction
    """

    def analyze(self, context):
        """
        Expected payload:
        {
            "data": ...,
            "model": callable
        }
        """
        data = context.get("data")
        model = context.get("model")

        self._remember(str(data))
        self._emit("sector_analysis_started", {"data": data})

        result = self.kernel.run_task(model, data)

        self._emit("sector_analysis_completed", {"result": result})
        return result


# =========================================================
# Planning Sector
# =========================================================

class PlanningSector(BaseSector):
    """
    Handles:
    - multi-step planning
    - reasoning
    - strategy generation
    """

    def plan(self, context):
        """
        Expected payload:
        {
            "steps": [
                {"model": callable, "inputs": ...},
                ...
            ]
        }
        """
        steps = context.get("steps", [])
        self._remember(str(steps))
        self._emit("sector_planning_started", {"steps": steps})

        results = []
        for step in steps:
            model = step.get("model")
            inputs = step.get("inputs")
            result = self.kernel.run_task(model, inputs)
            results.append(result)

        final = results[-1] if results else None

        self._emit("sector_planning_completed", {"result": final})
        return final


# =========================================================
# Knowledge Sector
# =========================================================

class KnowledgeSector(BaseSector):
    """
    Handles:
    - knowledge retrieval
    - memory search
    - fact extraction
    """

    def retrieve(self, context):
        """
        Expected payload:
        {
            "query": "..."
        }
        """
        query = context.get("query")
        self._remember(query)
        self._emit("sector_knowledge_started", {"query": query})

        results = self._recall(query)

        self._emit("sector_knowledge_completed", {"results": results})
        return results


# =========================================================
# Action Sector
# =========================================================

class ActionSector(BaseSector):
    """
    Handles:
    - task execution
    - action planning
    - operational logic
    """

    def execute(self, context):
        """
        Expected payload:
        {
            "model": callable,
            "inputs": ...
        }
        """
        model = context.get("model")
        inputs = context.get("inputs")

        self._remember(str(inputs))
        self._emit("sector_action_started", {"inputs": inputs})

        result = self.kernel.run_task(model, inputs)

        self._emit("sector_action_completed", {"result": result})
        return result
