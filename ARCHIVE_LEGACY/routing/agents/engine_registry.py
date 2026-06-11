from .engine_registry import ENGINE_REGISTRY

class EngineRouter:
    def __init__(self):
        self.engines = {k: v() for k, v in ENGINE_REGISTRY.items()}

    def route(self, task):
        engine = self.engines.get(task.type)
        if not engine:
            raise ValueError(f"No engine registered for type: {task.type}")
        return engine.run(task)
