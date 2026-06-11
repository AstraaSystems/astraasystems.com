class EngineTask:
    """
    Universal task object for all ASTRAA engines.
    """

    def __init__(self, task_type, payload, priority=5):
        self.type = task_type
        self.payload = payload
        self.priority = priority
        self.timestamp = None
        self.retries = 0
