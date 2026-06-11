class DecisionGate:
    def decide(self, fused):
        if fused.confidence < 0.55:
            return "HOLD (low confidence)"

        if fused.direction == "POSITIVE" and fused.score > 0.5:
            return "ACT POSITIVE"

        if fused.direction == "NEGATIVE" and fused.score < -0.5:
            return "ACT DEFENSIVE"

        return "MONITOR"
