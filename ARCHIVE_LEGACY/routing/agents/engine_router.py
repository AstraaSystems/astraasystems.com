from ardhanarishvara.routing.agents.engine_registry import ENGINE_REGISTRY

class EngineRouter:
    """
    Routes tasks to the correct ASTRAA engine (business, finance, construction)
    and ensures ARUHAN's execution layer handles the actual task execution.
    """

    def __init__(self):
        # Instantiate all registered engines
        self.engines = {name: engine_class() for name, engine_class in ENGINE_REGISTRY.items()}

    def route(self, task):
        """
        Route a task to the correct engine based on task.type.
        """
        engine = self.engines.get(task.type)

        if not engine:
            raise ValueError(f"No engine registered for task type: {task.type}")

        # Execute the task through the engine → ARUHAN execution bridge
        return engine.run(task)
