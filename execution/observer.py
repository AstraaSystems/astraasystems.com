import threading
import time
from queue import Queue


# =========================================================
# Observer Event Object
# =========================================================

class ObserverEvent:
    """
    Represents a system event that observers can react to.
    """
    def __init__(self, event_type, payload=None, timestamp=None):
        self.event_type = event_type
        self.payload = payload
        self.timestamp = timestamp or time.time()


# =========================================================
# Observer Registry
# =========================================================

class ObserverRegistry:
    """
    Stores all observers and dispatches events to them.
    Thread-safe.
    """

    def __init__(self):
        self.observers = {}
        self.lock = threading.Lock()

    def register(self, event_type, callback):
        """
        Register a callback for a specific event type.
        """
        with self.lock:
            if event_type not in self.observers:
                self.observers[event_type] = []
            self.observers[event_type].append(callback)

    def dispatch(self, event: ObserverEvent):
        """
        Dispatch event to all registered observers.
        """
        with self.lock:
            if event.event_type not in self.observers:
                return

            for callback in self.observers[event.event_type]:
                try:
                    callback(event)
                except Exception:
                    pass


# =========================================================
# Observer Engine (Event Loop)
# =========================================================

class ObserverEngine:
    """
    Central event engine that:
    - receives events
    - queues them
    - dispatches them to observers
    - runs in its own thread
    """

    def __init__(self):
        self.registry = ObserverRegistry()
        self.queue = Queue()
        self.running = False
        self.thread = None

    def start(self):
        """
        Start observer engine loop.
        """
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        """
        Stop observer engine.
        """
        self.running = False
        if self.thread:
            self.thread.join()

    def emit(self, event_type, payload=None):
        """
        Emit an event into the observer system.
        """
        event = ObserverEvent(event_type, payload)
        self.queue.put(event)

    def on(self, event_type, callback):
        """
        Register an observer callback.
        """
        self.registry.register(event_type, callback)

    def _loop(self):
        """
        Main event processing loop.
        """
        while self.running:
            try:
                event = self.queue.get(timeout=0.1)
                self.registry.dispatch(event)
            except Exception:
                pass


# =========================================================
# Global Observer Instance
# =========================================================

observer = ObserverEngine()
observer.start()
