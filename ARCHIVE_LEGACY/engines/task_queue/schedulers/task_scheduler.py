import time
from ardhanarishvara.engines.task_queue.queues.priority_queue import PriorityTaskQueue

class TaskScheduler:
    """
    Autonomous scheduler that feeds tasks to engine workers.
    """

    def __init__(self):
        self.queue = PriorityTaskQueue()

    def add_task(self, task):
        self.queue.push(task)

    def get_next_task(self):
        return self.queue.pop()

    def has_tasks(self):
        return not self.queue.empty()
