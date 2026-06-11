import time
from datetime import datetime, timedelta

class AutomationAnalytics:
    def __init__(self, observer, event_bus):
        self.observer = observer
        self.event_bus = event_bus

        # Counters for each AI
        self.arka_auto = 0
        self.arka_total = 0

        self.astraa_auto = 0
        self.astraa_total = 0

        self.aruhan_auto = 0
        self.aruhan_total = 0

        # Global counters
        self.global_auto = 0
        self.global_total = 0

        # Stability tracking
        self.stability_start = None
        self.stability_required = timedelta(hours=24)
        self.stability_active = False

        # Launch flag
        self.ready_for_launch = False
        self.commercial_launched = False

        # Subscribe to events
        self._subscribe()

    # ---------------------------------------------------------
    # EVENT SUBSCRIPTIONS
    # ---------------------------------------------------------
    def _subscribe(self):
        self.event_bus.subscribe("autonomous_action", self._handle_autonomous)
        self.event_bus.subscribe("manual_action", self._handle_manual)
        self.event_bus.subscribe("system_tick", self._check_stability)

    # ---------------------------------------------------------
    # EVENT HANDLERS
    # ---------------------------------------------------------
    def _handle_autonomous(self, data):
        ai = data.get("ai")

        if ai == "arka":
            self.arka_auto += 1
            self.arka_total += 1

        elif ai == "astraa":
            self.astraa_auto += 1
            self.astraa_total += 1

        elif ai == "aruhan":
            self.aruhan_auto += 1
            self.aruhan_total += 1

        self.global_auto += 1
        self.global_total += 1

        self._evaluate_readiness()

    def _handle_manual(self, data):
        ai = data.get("ai")

        if ai == "arka":
            self.arka_total += 1

        elif ai == "astraa":
            self.astraa_total += 1

        elif ai == "aruhan":
            self.aruhan_total += 1

        self.global_total += 1

        # Manual action breaks stability
        self._reset_stability()

    # ---------------------------------------------------------
    # AUTOMATION CALCULATIONS
    # ---------------------------------------------------------
    def _percent(self, auto, total):
        if total == 0:
            return 0
        return round((auto / total) * 100, 2)

    def get_automation_report(self):
        return {
            "arka": self._percent(self.arka_auto, self.arka_total),
            "astraa": self._percent(self.astraa_auto, self.astraa_total),
            "aruhan": self._percent(self.aruhan_auto, self.aruhan_total),
            "global": self._percent(self.global_auto, self.global_total),
            "stability_active": self.stability_active,
            "stability_elapsed": self._stability_elapsed(),
            "ready_for_launch": self.ready_for_launch,
            "commercial_launched": self.commercial_launched
        }

    # ---------------------------------------------------------
    # READINESS + STABILITY LOGIC
    # ---------------------------------------------------------
    def _evaluate_readiness(self):
        arka = self._percent(self.arka_auto, self.arka_total)
        astraa = self._percent(self.astraa_auto, self.astraa_total)
        aruhan = self._percent(self.aruhan_auto, self.aruhan_total)

        # All 3 must be 100%
        if arka == 100 and astraa == 100 and aruhan == 100:
            if not self.stability_active:
                self.stability_start = datetime.now()
                self.stability_active = True
                self.observer.emit("stability_started", {})
        else:
            self._reset_stability()

    def _reset_stability(self):
        self.stability_active = False
        self.stability_start = None

    def _stability_elapsed(self):
        if not self.stability_active or not self.stability_start:
            return timedelta(0)
        return datetime.now() - self.stability_start

    # ---------------------------------------------------------
    # STABILITY CHECK (RUNS EVERY MINUTE)
    # ---------------------------------------------------------
    def _check_stability(self, _):
        if not self.stability_active:
            return

        if self._stability_elapsed() >= self.stability_required:
            self.ready_for_launch = True
            self._trigger_commercial_launch()

    # ---------------------------------------------------------
    # COMMERCIAL LAUNCH
    # ---------------------------------------------------------
    def _trigger_commercial_launch(self):
        if self.commercial_launched:
            return

        self.commercial_launched = True

        # Notify the ecosystem
        self.observer.emit("commercial_launch", {
            "timestamp": datetime.now().isoformat()
        })

        # Notify ARKA HQ
        self.event_bus.publish("arka_notify", {
            "message": "Partner, the Big 3 have maintained 100% automation for 24 hours. "
                       "Commercial engines have been activated. The 15-day trial cycle has begun."
        })

        # Notify Android HQ interface
        self.event_bus.publish("hq_mobile_update", {
            "status": "Commercial Mode Active",
            "timestamp": datetime.now().isoformat()
        })
