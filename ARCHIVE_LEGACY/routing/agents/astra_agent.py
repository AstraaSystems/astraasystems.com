from ardhanarishvara.astra.astra_core import AstraCore
from ardhanarishvara.routing.task_router import router
from ardhanarishvara.engines.task_queue.task_queue_manager import TaskQueueManager

self.task_queue = TaskQueueManager()

def astra_handler(task):
    core = AstraCore()
    goal = task.get("task", "")
    return core.execute_goal(goal)

router.register_agent("astra", astra_handler)
