import math
from aruhan.governance.fusion.signal_models import Signal

class DataOracle:
    def build_signal(self, measurement, recent_measurements):
        if len(recent_measurements) < 2:
            return Signal(source="dataoracle", value=0.0, confidence=0.5, trend="STABLE")

        delta = recent_measurements[-1] - recent_measurements[-2]
        value = max(-1.0, min(1.0, delta / 0.5))

        if len(recent_measurements) >= 5:
            window = recent_measurements[-5:]
            mean_ = sum(window) / len(window)
            vol = math.sqrt(sum((x - mean_) ** 2 for x in window) / len(window))
        else:
            vol = 0.0

        regime = "VOLATILE" if vol > 0.20 else "NORMAL"
        trend = "IMPROVING" if delta > 0.05 else ("DECLINING" if delta < -0.05 else "STABLE")
        confidence = 0.75 if regime == "NORMAL" else 0.60

        return Signal(source="dataoracle", value=value, confidence=confidence, trend=trend, regime=regime)
