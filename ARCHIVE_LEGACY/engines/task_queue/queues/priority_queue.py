import heapq
import time

class PriorityTaskQueue:
    """
    Priority-based task queue for autonomous engine scheduling.
    """

    def __init__(self):
        self.queue = []

    def push(self, task):
        task.timestamp = time.time()
        heapq.heappush(self.queue, (task.priority, task.timestamp, task))

    def pop(self):
        if not self.queue:
            return None
        return heapq.heappop(self.queue)[2]

    def empty(self):
        return len(self.queue) == 0
