import time
from ardhanarishvara.routing.agents.engine_router import EngineRouter

class EngineWorker:
    """
    Worker that autonomously pulls tasks from the scheduler and executes them.
    """

    def __init__(self, scheduler, interval=0.5):
        self.scheduler = scheduler
        self.router = EngineRouter()
        self.interval = interval

    def start(self):
        while True:
            if self.scheduler.has_tasks():
                task = self.scheduler.get_next_task()
                self.router.route(task)
            time.sleep(self.interval)
