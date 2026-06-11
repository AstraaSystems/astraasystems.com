from aruhan.governance.fusion.signal_models import Signal

class ReflectionEngine:
    def __init__(self):
        self.history = []

    def reflect(self, prediction, actual, confidence):
        error = abs(prediction - actual)
        record = {"prediction": prediction, "actual": actual, "error": error, "confidence": confidence}
        self.history.append(record)

        if error > 0.20:
            return "HIGH_ERROR", record
        elif error > 0.08:
            return "MEDIUM_ERROR", record
        return "LOW_ERROR", record

    def latest_error_signal(self):
        if not self.history:
            return Signal(source="reflection", value=0.0, confidence=0.5, trend="STABLE", note="No history")

        recent = self.history[-1]
        error = recent["error"]
        value = -min(1.0, error)
        conf = min(0.95, 0.6 + len(self.history) * 0.01)

        trend = "STABLE"
        if len(self.history) >= 3:
            last3 = [x["error"] for x in self.history[-3:]]
            if last3[-1] > sum(last3[:-1]) / 2:
                trend = "DECLINING"

        return Signal(source="reflection", value=value, confidence=conf, trend=trend, note=f"error={error:.4f}")
