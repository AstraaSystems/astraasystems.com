from aruhan.governance.fusion.signal_models import Signal

class TemporalEngine:
    def __init__(self):
        self.accuracy_history = []

    def update(self, accuracy_score):
        self.accuracy_history.append(accuracy_score)
        if len(self.accuracy_history) > 50:
            self.accuracy_history.pop(0)

    def recent_trend(self):
        if len(self.accuracy_history) < 5:
            return "STABLE"
        recent = sum(self.accuracy_history[-5:]) / 5
        overall = sum(self.accuracy_history) / len(self.accuracy_history)

        if recent < overall - 0.03:
            return "DECLINING"
        elif recent > overall + 0.03:
            return "IMPROVING"
        return "STABLE"

    def temporal_signal(self):
        if not self.accuracy_history:
            return Signal(source="temporal", value=0.0, confidence=0.5, trend="STABLE", note="No history")

        avg_acc = sum(self.accuracy_history) / len(self.accuracy_history)
        value = (avg_acc * 2.0) - 1.0

        return Signal(source="temporal", value=max(-1.0, min(1.0, value)), confidence=min(0.95, 0.55 + len(self.accuracy_history) * 0.01), trend=self.recent_trend())
