import time
import threading
import statistics
from collections import deque, defaultdict

from ardhanarishvara.execution.observer import observer


# =========================================================
# ARUHAN Analytics Engine
# =========================================================

class ARUHANAnalyticsEngine:
    """
    Analytics engine for Ardhanarishvara OS.

    Responsibilities:
    - collect system metrics
    - analyze performance
    - detect anomalies
    - generate insights
    - feed analytics back into ARUHAN
    """

    def __init__(self, window_size=100):
        self.window_size = window_size

        # Rolling metrics
        self.metrics = {
            "task_latency": deque(maxlen=window_size),
            "task_failures": deque(maxlen=window_size),
            "sector_usage": defaultdict(int),
            "engine_usage": defaultdict(int),
            "memory_events": deque(maxlen=window_size),
        }

        # Thread safety
        self.lock = threading.Lock()

        # Subscribe to observer events
        observer.on("task_completed", self._on_task_completed)
        observer.on("task_failed", self._on_task_failed)
        observer.on("sector_comm_completed", self._on_sector_event)
        observer.on("sector_analysis_completed", self._on_sector_event)
        observer.on("sector_planning_completed", self._on_sector_event)
        observer.on("sector_knowledge_completed", self._on_sector_event)
        observer.on("sector_action_completed", self._on_sector_event)
        observer.on("memory_write", self._on_memory_event)

    # -----------------------------------------------------
    # Observer Event Handlers
    # -----------------------------------------------------
    def _on_task_completed(self, event):
        with self.lock:
            latency = event.payload.get("latency", 0.0)
            self.metrics["task_latency"].append(latency)

    def _on_task_failed(self, event):
        with self.lock:
            self.metrics["task_failures"].append(1)

    def _on_sector_event(self, event):
        with self.lock:
            sector = event.payload.get("sector")
            if sector:
                self.metrics["sector_usage"][sector] += 1

    def _on_memory_event(self, event):
        with self.lock:
            self.metrics["memory_events"].append(event.payload)

    # -----------------------------------------------------
    # Compute Analytics
    # -----------------------------------------------------
    def compute(self):
        with self.lock:
            latency_data = list(self.metrics["task_latency"])
            failure_data = list(self.metrics["task_failures"])

            avg_latency = statistics.mean(latency_data) if latency_data else 0.0
            max_latency = max(latency_data) if latency_data else 0.0
            failure_rate = sum(failure_data) / len(failure_data) if failure_data else 0.0

            sector_load = dict(self.metrics["sector_usage"])

            return {
                "avg_latency": avg_latency,
                "max_latency": max_latency,
                "failure_rate": failure_rate,
                "sector_load": sector_load,
                "memory_events": len(self.metrics["memory_events"]),
            }

    # -----------------------------------------------------
    # Generate Insights
    # -----------------------------------------------------
    def insights(self):
        data = self.compute()

        insights = []

        if data["avg_latency"] > 1.0:
            insights.append("System latency is increasing — consider scaling concurrency.")

        if data["failure_rate"] > 0.1:
            insights.append("High task failure rate detected — investigate model stability.")

        if data["max_latency"] > 5.0:
            insights.append("Severe latency spikes detected — potential bottleneck.")

        if data["sector_load"]:
            busiest = max(data["sector_load"], key=data["sector_load"].get)
            insights.append(f"Most active sector: {busiest}")

        if data["memory_events"] > 50:
            insights.append("High memory write frequency — consider summarization.")

        return {
            "analytics": data,
            "insights": insights
        }

    # -----------------------------------------------------
    # Periodic Analytics Loop
    # -----------------------------------------------------
    def start(self, interval=10):
        self.running = True
        self.thread = threading.Thread(target=self._loop, args=(interval,), daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if hasattr(self, "thread"):
            self.thread.join()

    def _loop(self, interval):
        while self.running:
            result = self.insights()
            observer.emit("analytics_update", result)
            time.sleep(interval)
