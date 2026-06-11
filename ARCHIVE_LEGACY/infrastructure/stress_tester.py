import time
import threading
import random
import traceback

class ARKAStressTester:
    """
    ARKA Stability Phase v1 - Stress Tester
    Simulates:
    - High event load
    - High command load
    - High cloud sync frequency
    - High metrics collection
    - Random burst patterns
    """

    def __init__(self, core):
        self.core = core
        self.running = False
        self.mode = "normal"  # normal, burst, sustained, spike
        self.interval = 1     # seconds

    # ---------------------------------------------------------
    # START STRESS TESTER
    # ---------------------------------------------------------
    def start(self, mode="normal"):
        self.mode = mode
        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print(f"[STRESS] Stress Tester online (mode: {mode}).")

    # ---------------------------------------------------------
    # STOP STRESS TESTER
    # ---------------------------------------------------------
    def stop(self):
        self.running = False
        print("[STRESS] Stress Tester offline.")

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------
    def _loop(self):
        while self.running:
            try:
                if self.mode == "normal":
                    self._normal_load()

                elif self.mode == "burst":
                    self._burst_load()

                elif self.mode == "sustained":
                    self._sustained_load()

                elif self.mode == "spike":
                    self._spike_load()

            except Exception as e:
                print("[STRESS] ERROR:", e)
                traceback.print_exc()

            time.sleep(self.interval)

    # ---------------------------------------------------------
    # LOAD PATTERNS
    # ---------------------------------------------------------
    def _normal_load(self):
        self._stress_events(5)
        self._stress_commands(2)
        self._stress_metrics()
        self._stress_cloud()

    def _burst_load(self):
        self._stress_events(50)
        self._stress_commands(10)
        self._stress_metrics()
        self._stress_cloud()

    def _sustained_load(self):
        self._stress_events(20)
        self._stress_commands(5)
        self._stress_metrics()
        self._stress_cloud()

    def _spike_load(self):
        self._stress_events(200)
        self._stress_commands(20)
        self._stress_metrics()
        self._stress_cloud()

    # ---------------------------------------------------------
    # STRESS ACTIONS
    # ---------------------------------------------------------
    def _stress_events(self, count):
        for _ in range(count):
            event_name = random.choice(["tick", "update", "heartbeat", "module_ping"])
            self.core.event_bus.publish(event_name, {"load": random.randint(1, 100)})

    def _stress_commands(self, count):
        for _ in range(count):
            cmd = random.choice(["status", "modules", "cloud_sync"])
            self.core.command_engine.execute(self.core.permissions.admin_token, cmd)

    def _stress_metrics(self):
        self.core.metrics.collect()

    def _stress_cloud(self):
        self.core.cloud._sync()
