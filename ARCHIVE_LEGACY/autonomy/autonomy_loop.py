import time
import threading

class AutonomyLoop:
    """
    AUTONOMY LOOP
    Allows Aruhan to think independently:
    - background emotional processing
    - mood drift
    - internal state updates
    - emotional digestion (non-linear latency)
    - proactive checks
    """

    def __init__(self, aruhan_core):
        self.aruhan = aruhan_core
        self.running = False
        self.thread = None
        self.interval = 5  # seconds between autonomous cycles

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            try:
                # Emotional digestion: slow internal processing
                self._emotional_digestion()

                # Mood drift: slow natural changes
                self._mood_drift()

                # Internal clarity/stability adjustments
                self._update_internal_state()

            except Exception as e:
                print("Autonomy Loop Error:", e)

            time.sleep(self.interval)

    def _emotional_digestion(self):
        # Emotional digestion increases latency factor slowly
        self.aruhan.latency_factor = min(
            self.aruhan.latency_factor + 0.05,
            2.0
        )

    def _mood_drift(self):
        # Mood drifts toward neutral over time
        current = self.aruhan.mood_engine._mood_to_value(self.aruhan.mood)
        if current > 0:
            current -= 0.1
        elif current < 0:
            current += 0.1

        self.aruhan.mood = self.aruhan.mood_engine._value_to_mood(current)

    def _update_internal_state(self):
        # Stability and clarity slowly recover
        self.aruhan.internal_state["stability"] = min(
            self.aruhan.internal_state["stability"] + 0.01,
            1.0
        )
        self.aruhan.internal_state["clarity"] = min(
            self.aruhan.internal_state["clarity"] + 0.01,
            1.0
        )
