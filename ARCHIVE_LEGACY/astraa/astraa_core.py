# -------------------------------------------------------------
# ASTRAA CORE — FULL INTEGRATED VERSION
# -------------------------------------------------------------

import traceback
from datetime import datetime

class ASTRAACore:
    def __init__(self, observer, event_bus, analytics, sectors, engines):
        self.observer = observer
        self.event_bus = event_bus
        self.analytics = analytics

        # Sectors = dict of sector_name → sector_instance
        self.sectors = sectors

        # Engines = dict of engine_name → engine_instance
        self.engines = engines

        # Subscribe to events
        self.event_bus.subscribe("commercial_launch", self._handle_commercial_launch)
        self.event_bus.subscribe("sector_autonomous", self._handle_sector_autonomous)
        self.event_bus.subscribe("sector_manual", self._handle_sector_manual)
        self.event_bus.subscribe("engine_autonomous", self._handle_engine_autonomous)
        self.event_bus.subscribe("engine_manual", self._handle_engine_manual)

    # ---------------------------------------------------------
    # MAIN ENTRY POINT FOR TASKS FROM ARKA
    # ---------------------------------------------------------
    def handle_task(self, task):
        # Manual action (task came from ARKA)
        self.event_bus.publish("manual_action", {"ai": "astraa"})

        try:
            sector = task.get("sector")
            payload = task.get("payload")

            if sector not in self.sectors:
                raise ValueError(f"Unknown sector: {sector}")

            result = self.sectors[sector].execute(payload)

            self.observer.emit("astraa_task_completed", {
                "sector": sector,
                "timestamp": datetime.now().isoformat()
            })

            return result

        except Exception as e:
            self._handle_error(e)
            return None

    # ---------------------------------------------------------
    # AUTONOMOUS TASK HANDLING
    # ---------------------------------------------------------
    def handle_autonomous_task(self, sector, payload):
        # Autonomous action
        self.event_bus.publish("autonomous_action", {"ai": "astraa"})

        try:
            if sector not in self.sectors:
                raise ValueError(f"Unknown sector: {sector}")

            result = self.sectors[sector].execute(payload)

            self.observer.emit("astraa_autonomous", {
                "sector": sector,
                "timestamp": datetime.now().isoformat()
            })

            return result

        except Exception as e:
            self._handle_error(e)
            return None

    # ---------------------------------------------------------
    # ENGINE EXECUTION
    # ---------------------------------------------------------
    def run_engine(self, engine_name, payload, autonomous=False):
        if engine_name not in self.engines:
            raise ValueError(f"Unknown engine: {engine_name}")

        # Emit correct analytics event
        if autonomous:
            self.event_bus.publish("autonomous_action", {"ai": "astraa"})
        else:
            self.event_bus.publish("manual_action", {"ai": "astraa"})

        try:
            result = self.engines[engine_name].run(payload)

            self.observer.emit("astraa_engine_run", {
                "engine": engine_name,
                "autonomous": autonomous,
                "timestamp": datetime.now().isoformat()
            })

            return result

        except Exception as e:
            self._handle_error(e)
            return None

    # ---------------------------------------------------------
    # SECTOR + ENGINE FORWARDING TO ANALYTICS
    # ---------------------------------------------------------
    def _handle_sector_autonomous(self, data):
        self.event_bus.publish("autonomous_action", {"ai": "astraa"})

    def _handle_sector_manual(self, data):
        self.event_bus.publish("manual_action", {"ai": "astraa"})

    def _handle_engine_autonomous(self, data):
        self.event_bus.publish("autonomous_action", {"ai": "astraa"})

    def _handle_engine_manual(self, data):
        self.event_bus.publish("manual_action", {"ai": "astraa"})

    # ---------------------------------------------------------
    # ERROR HANDLING (BREAKS STABILITY)
    # ---------------------------------------------------------
    def _handle_error(self, error):
        # Manual action (fallback)
        self.event_bus.publish("manual_action", {"ai": "astraa"})

        self.observer.emit("astraa_error", {
            "error": str(error),
            "trace": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        })

    # ---------------------------------------------------------
    # COMMERCIAL LAUNCH EVENT HANDLER
    # ---------------------------------------------------------
    def _handle_commercial_launch(self, data):
        self.observer.emit("astraa_event", {
            "type": "commercial_launch_notice",
            "timestamp": data["timestamp"]
        })

        # ASTRAA does not activate engines — ARUHAN does.
        # ASTRAA only acknowledges the event.

    # ---------------------------------------------------------
    # AUTOMATION STATUS REPORTING
    # ---------------------------------------------------------
    def get_automation_status(self):
        return self.analytics.get_automation_report()
