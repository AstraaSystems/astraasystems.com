import time
import json
import os
import traceback

class ARKAStabilityReporter:
    """
    ARKA Stability Phase v1 - Stability Reporter
    Generates:
    - Uptime reports
    - Error summaries
    - Module health summaries
    - Cloud sync summaries
    - Security integrity summaries
    - Performance snapshots
    - Stability score
    """

    def __init__(self, core):
        self.core = core
        self.start_time = time.time()
        self.report_path = "/home/keshanth/ARKA/logs/stability_report.json"
        self.interval = 30  # seconds
        self.running = False

    # ---------------------------------------------------------
    # START REPORTER
    # ---------------------------------------------------------
    def start(self):
        self.running = True
        import threading
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print("[REPORTER] Stability Reporter online.")

    # ---------------------------------------------------------
    # STOP REPORTER
    # ---------------------------------------------------------
    def stop(self):
        self.running = False
        print("[REPORTER] Stability Reporter offline.")

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------
    def _loop(self):
        while self.running:
            try:
                report = self.generate_report()
                self._write_report(report)
            except Exception as e:
                print("[REPORTER] ERROR:", e)
                traceback.print_exc()

            time.sleep(self.interval)

    # ---------------------------------------------------------
    # REPORT GENERATION
    # ---------------------------------------------------------
    def generate_report(self):
        uptime = time.time() - self.start_time
        metrics = self.core.metrics.collect()
        module_health = self.core.registry.check_health()
        integrity_ok = self.core.security.verify_integrity()

        # Stability score (simple v1 formula)
        score = 100
        if not integrity_ok:
            score -= 40
        if metrics["memory_usage"] > 90:
            score -= 20
        if metrics["cpu_usage"] > 90:
            score -= 20
        if any(not ok for ok in module_health.values()):
            score -= 20

        report = {
            "timestamp": time.time(),
            "uptime_seconds": uptime,
            "cpu_usage": metrics["cpu_usage"],
            "memory_usage": metrics["memory_usage"],
            "runtime_tick": metrics["runtime_tick"],
            "event_tick": metrics["event_tick"],
            "scheduler_tick": metrics["scheduler_tick"],
            "event_throughput": metrics["event_throughput"],
            "module_health": module_health,
            "integrity_ok": integrity_ok,
            "stability_score": max(score, 0)
        }

        return report

    # ---------------------------------------------------------
    # WRITE REPORT TO FILE
    # ---------------------------------------------------------
    def _write_report(self, report):
        try:
            with open(self.report_path, "w") as f:
                json.dump(report, f, indent=4)
            print("[REPORTER] Stability report updated.")
        except Exception as e:
            print("[REPORTER] Failed to write report:", e)
