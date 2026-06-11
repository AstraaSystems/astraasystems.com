# -------------------------------------------------------------
# ARKA CORE — FULL INTEGRATED VERSION
# -------------------------------------------------------------

import traceback
from datetime import datetime

class ARKACore:
    def __init__(self, observer, event_bus, analytics, router, memory):
        self.observer = observer
        self.event_bus = event_bus
        self.analytics = analytics
        self.router = router
        self.memory = memory

        # Subscribe to events
        self.event_bus.subscribe("commercial_launch", self._handle_commercial_launch)
        self.event_bus.subscribe("sector_autonomous", self._handle_sector_autonomous)
        self.event_bus.subscribe("sector_manual", self._handle_sector_manual)
        self.event_bus.subscribe("engine_autonomous", self._handle_engine_autonomous)
        self.event_bus.subscribe("engine_manual", self._handle_engine_manual)

    # ---------------------------------------------------------
    # MAIN ENTRY POINT FOR USER COMMANDS
    # ---------------------------------------------------------
    def handle_user_command(self, command):
        # Manual action
        self.event_bus.publish("manual_action", {"ai": "arka"})

        try:
            self.observer.emit("arka_received", {
                "command": command,
                "timestamp": datetime.now().isoformat()
            })

            # Intent resolution
            intent = self._resolve_intent(command)

            # Routing
            result = self._route_intent(intent)

            # Memory update
            self.memory.store_interaction(command, result)

            return result

        except Exception as e:
            self._handle_error(e)
            return "An internal error occurred."

    # ---------------------------------------------------------
    # AUTONOMOUS COMMAND HANDLING
    # ---------------------------------------------------------
    def handle_autonomous_command(self, intent):
        # Autonomous action
        self.event_bus.publish("autonomous_action", {"ai": "arka"})

        try:
            result = self._route_intent(intent)

            self.observer.emit("arka_autonomous", {
                "intent": intent,
                "timestamp": datetime.now().isoformat()
            })

            return result

        except Exception as e:
            self._handle_error(e)
            return None

    # ---------------------------------------------------------
    # INTENT RESOLUTION
    # ---------------------------------------------------------
    def _resolve_intent(self, command):
        # Autonomous action (ARKA resolves intent without help)
        self.event_bus.publish("autonomous_action", {"ai": "arka"})

        # Simple placeholder — your real intent engine goes here
        return {"type": "task", "payload": command}

    # ---------------------------------------------------------
    # ROUTING LOGIC
    # ---------------------------------------------------------
    def _route_intent(self, intent):
        # Autonomous action (ARKA routes without help)
        self.event_bus.publish("autonomous_action", {"ai": "arka"})

        return self.router.route(intent)

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
        # Manual action (error = fallback)
        self.event_bus.publish("manual_action", {"ai": "arka"})

        self.observer.emit("arka_error", {
            "error": str(error),
            "trace": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        })

    # ---------------------------------------------------------
    # COMMERCIAL LAUNCH EVENT HANDLER
    # ---------------------------------------------------------
    def _handle_commercial_launch(self, data):
        self.observer.emit("arka_event", {
            "type": "commercial_launch_notice",
            "timestamp": data["timestamp"]
        })

        # Notify user
        self.event_bus.publish("arka_notify", {
            "message": "Partner, the Big 3 have maintained 100% automation for 24 hours. "
                       "Commercial engines are now active. The 15-day trial cycle has begun."
        })

    # ---------------------------------------------------------
    # AUTOMATION STATUS REPORTING
    # ---------------------------------------------------------
    def get_automation_status(self):
        return self.analytics.get_automation_report()
