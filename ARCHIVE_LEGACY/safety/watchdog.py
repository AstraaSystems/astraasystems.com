import time
import threading
import traceback

class ARKAWatchdog:
    """
    ARKA Self-Monitoring System (Watchdog)
    Monitors runtime, event loop, scheduler, memory, and module health.
    """

    def __init__(self, core):
        self.core = core
        self.running = False
        self.last_runtime_tick = 0
        self.last_event_tick = 0
        self.last_scheduler_tick = 0
        self.health_log = []

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print("[WATCHDOG] Watchdog online.")

    def stop(self):
        self.running = False
        print("[WATCHDOG] Watchdog offline.")

    def _loop(self):
        while self.running:
            try:
                self._check_runtime()
                self._check_event_loop()
                self._check_scheduler()
                self._check_memory()
                self._check_modules()
            except Exception as e:
                print("[WATCHDOG] ERROR:", e)
                traceback.print_exc()

            time.sleep(2)

    def _check_runtime(self):
        tick = self.core.state.runtime_tick
        if tick == self.last_runtime_tick:
            print("[WATCHDOG] Runtime freeze detected.")
            self._trigger_repair("runtime")
        self.last_runtime_tick = tick

    def _check_event_loop(self):
        tick = self.core.state.event_tick
        if tick == self.last_event_tick:
            print("[WATCHDOG] Event loop freeze detected.")
            self._trigger_repair("event_loop")
        self.last_event_tick = tick

    def _check_scheduler(self):
        tick = self.core.state.scheduler_tick
        if tick == self.last_scheduler_tick:
            print("[WATCHDOG] Scheduler freeze detected.")
            self._trigger_repair("scheduler")
        self.last_scheduler_tick = tick

    def _check_memory(self):
        mem = self.core.state.memory_usage
        if mem > 90:
            print("[WATCHDOG] High memory usage detected.")
            self._trigger_repair("memory")

    def _check_modules(self):
        for name, module in self.core.modules.items():
            if not module.healthy:
                print(f"[WATCHDOG] Module failure detected: {name}")
                self._trigger_repair(f"module:{name}")

    def _trigger_repair(self, issue):
        print(f"[WATCHDOG] Triggering repair for: {issue}")
        self.health_log.append(issue)
        self.core.repair_engine.handle(issue)
