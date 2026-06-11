from ardhanarishvara.engines.task_queue.schedulers.task_scheduler import TaskScheduler
from ardhanarishvara.engines.task_queue.workers.engine_worker import EngineWorker

class TaskQueueManager:
    """
    Central manager for autonomous engine task execution.
    """

    def __init__(self):
        self.scheduler = TaskScheduler()
        self.worker = EngineWorker(self.scheduler)

    def submit(self, task):
        self.scheduler.add_task(task)

    def start(self):
        self.worker.start()
