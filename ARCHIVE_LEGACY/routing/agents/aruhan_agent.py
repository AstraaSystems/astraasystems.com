from ardhanarishvara.routing.agents.engine_router import EngineRouter
from ardhanarishvara.engines.task_queue.task_queue_manager import TaskQueueManager

self.task_queue = TaskQueueManager()

class AruhanAgent:
    def __init__(self):
        self.engine_router = EngineRouter()

    def execute(self, task):
        return self.engine_router.route(task)
