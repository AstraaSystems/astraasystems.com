# -------------------------------------------------------------
# MULTI-AGENT CORE — FULL INTEGRATED VERSION
# -------------------------------------------------------------

import traceback
from datetime import datetime

class MultiAgentCore:
    def __init__(self, observer, event_bus, analytics, agent_classes):
        self.observer = observer
        self.event_bus = event_bus
        self.analytics = analytics

        # agent_classes = dict of agent_name → agent_class
        self.agent_classes = agent_classes
        self.agents = {}

        # Subscribe to events
        self.event_bus.subscribe("commercial_launch", self._handle_commercial_launch)
        self.event_bus.subscribe("agent_autonomous", self._handle_agent_autonomous)
        self.event_bus.subscribe("agent_manual", self._handle_agent_manual)

    # ---------------------------------------------------------
    # INITIALIZE ALL AGENTS
    # ---------------------------------------------------------
    def initialize_agents(self):
        for name, cls in self.agent_classes.items():
            try:
                self.agents[name] = cls(self.event_bus, self.observer)
                self.observer.emit("agent_initialized", {
                    "agent": name,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self._handle_error(e)

    # ---------------------------------------------------------
    # MANUAL TASK DISPATCH
    # ---------------------------------------------------------
    def dispatch_manual(self, agent_name, task):
        # Manual action
        self.event_bus.publish("manual_action", {"ai": "astraa"})

        try:
            if agent_name not in self.agents:
                raise ValueError(f"Unknown agent: {agent_name}")

            result = self.agents[agent_name].handle_task(task)

            self.observer.emit("agent_task_completed", {
                "agent": agent_name,
                "manual": True,
                "timestamp": datetime.now().isoformat()
            })

            return result

        except Exception as e:
            self._handle_error(e)
            return None

    # ---------------------------------------------------------
    # AUTONOMOUS TASK DISPATCH
    # ---------------------------------------------------------
    def dispatch_autonomous(self, agent_name, task):
        # Autonomous action
        self.event_bus.publish("autonomous_action", {"ai": "astraa"})

        try:
            if agent_name not in self.agents:
                raise ValueError(f"Unknown agent: {agent_name}")

            result = self.agents[agent_name].handle_autonomous(task)

            self.observer.emit("agent_task_completed", {
                "agent": agent_name,
                "manual": False,
                "timestamp": datetime.now().isoformat()
            })

            return result

        except Exception as e:
            self._handle_error(e)
            return None

    # ---------------------------------------------------------
    # AGENT EVENT FORWARDING TO ANALYTICS
    # ---------------------------------------------------------
    def _handle_agent_autonomous(self, data):
        self.event_bus.publish("autonomous_action", {"ai": "astraa"})

    def _handle_agent_manual(self, data):
        self.event_bus.publish("manual_action", {"ai": "astraa"})

    # ---------------------------------------------------------
    # ERROR HANDLING (BREAKS STABILITY)
    # ---------------------------------------------------------
    def _handle_error(self, error):
        # Manual action (fallback)
        self.event_bus.publish("manual_action", {"ai": "astraa"})

        self.observer.emit("multiagent_error", {
            "error": str(error),
            "trace": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        })

    # ---------------------------------------------------------
    # COMMERCIAL LAUNCH EVENT HANDLER
    # ---------------------------------------------------------
    def _handle_commercial_launch(self, data):
        self.observer.emit("multiagent_event", {
            "type": "commercial_launch_notice",
            "timestamp": data["timestamp"]
        })

        # Agents do not activate engines — ARUHAN does.
        # Multi-agent mode only acknowledges the event.

    # ---------------------------------------------------------
    # AUTOMATION STATUS REPORTING
    # ---------------------------------------------------------
    def get_automation_status(self):
        return self.analytics.get_automation_report()
