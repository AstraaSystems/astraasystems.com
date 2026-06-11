"""
ARKA Agent Registration — Permanent Version
"""

from ARKA.core.arka_core import ArkaCore
from ARKA.mock_ai import MockAI
from ardhanarishvara.routing.task_router import router
from ardhanarishvara.engines.task_queue.task_queue_manager import TaskQueueManager
from ardhanarishvara.engines.task_queue.task import EngineTask

self.task_queue = TaskQueueManager()

def queue_task(self, task_type, payload, priority=5):
    task = EngineTask(task_type, payload, priority)
    self.task_queue.submit(task)

def arka_handler(task):
    core = ArkaCore(MockAI())
    goal = task.get("task", "")
    return core.execute_goal(goal)

router.register_agent("arka", arka_handler)
