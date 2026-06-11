import threading
from ardhanarishvara.execution.observer import observer


# =========================================================
# Task Router
# =========================================================

class TaskRouter:
    """
    Central routing system that:
    - receives tasks
    - determines destination engine/sector
    - dispatches tasks
    - emits observer events
    """

    def __init__(self):
        self.engine_adapters = {}
        self.sector_adapters = {}
        self.lock = threading.Lock()

    # -----------------------------------------------------
    # Register Engine Adapter
    # -----------------------------------------------------
    def register_engine(self, name, adapter):
        with self.lock:
            self.engine_adapters[name] = adapter
            observer.emit("engine_registered", {"engine": name})

    # -----------------------------------------------------
    # Register Sector Adapter
    # -----------------------------------------------------
    def register_sector(self, name, adapter):
        with self.lock:
            self.sector_adapters[name] = adapter
            observer.emit("sector_registered", {"sector": name})

    # -----------------------------------------------------
    # Route Task
    # -----------------------------------------------------
    def route(self, target, payload):
        """
        target format:
            engine:<name>
            sector:<name>
        """
        observer.emit("task_routed", {"target": target})

        if target.startswith("engine:"):
            name = target.split("engine:")[1]
            return self._route_engine(name, payload)

        if target.startswith("sector:"):
            name = target.split("sector:")[1]
            return self._route_sector(name, payload)

        raise ValueError(f"Unknown routing target: {target}")

    # -----------------------------------------------------
    # Engine Routing
    # -----------------------------------------------------
    def _route_engine(self, name, payload):
        with self.lock:
            if name not in self.engine_adapters:
                observer.emit("routing_error", {"engine": name})
                raise RuntimeError(f"Engine '{name}' not registered")

            adapter = self.engine_adapters[name]
            return adapter.handle(payload)

    # -----------------------------------------------------
    # Sector Routing
    # -----------------------------------------------------
    def _route_sector(self, name, payload):
        with self.lock:
            if name not in self.sector_adapters:
                observer.emit("routing_error", {"sector": name})
                raise RuntimeError(f"Sector '{name}' not registered")

            adapter = self.sector_adapters[name]
            return adapter.handle(payload)


# =========================================================
# Engine Adapter
# =========================================================

class EngineAdapter:
    """
    Wraps an engine and exposes a unified handle() interface.
    """

    def __init__(self, engine):
        self.engine = engine

    def handle(self, payload):
        """
        Engines receive structured payloads:
        {
            "task": "...",
            "data": {...}
        }
        """
        task = payload.get("task")
        data = payload.get("data")

        if not hasattr(self.engine, task):
            raise RuntimeError(f"Engine missing task handler: {task}")

        method = getattr(self.engine, task)
        return method(data)


# =========================================================
# Sector Adapter
# =========================================================

class SectorAdapter:
    """
    Wraps a sector and exposes a unified handle() interface.
    """

    def __init__(self, sector):
        self.sector = sector

    def handle(self, payload):
        """
        Sectors receive structured payloads:
        {
            "intent": "...",
            "context": {...}
        }
        """
        intent = payload.get("intent")
        context = payload.get("context")

        if not hasattr(self.sector, intent):
            raise RuntimeError(f"Sector missing intent handler: {intent}")

        method = getattr(self.sector, intent)
        return method(context)
