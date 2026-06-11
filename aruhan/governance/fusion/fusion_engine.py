from typing import List
from .signal_models import Signal
from aruhan.governance.fusion.signal_models import FusionResult

class FusionEngine:
    def fuse(self, signals):
        if not signals:
            return FusionResult(0.0, 0.0, "NEUTRAL", 0.0, 0.0)

        total_weight = 0.0
        weighted_sum = 0.0
        confidence_sum = 0.0

        for s in signals:
            total_weight += s.trust_weight
            weighted_sum += s.value * s.trust_weight
            confidence_sum += s.confidence * s.trust_weight

        if total_weight == 0:
            return FusionResult(0.0, 0.0, "NEUTRAL", 0.0, 1.0)

        score = weighted_sum / total_weight
        confidence = confidence_sum / total_weight

        if score > 0.2:
            direction = "POSITIVE"
        elif score < -0.2:
            direction = "NEGATIVE"
        else:
            direction = "NEUTRAL"

        agreement = self._compute_agreement(signals)
        instability = self._compute_instability(signals)

        return FusionResult(score, confidence, direction, agreement, instability)

    def _compute_agreement(self, signals):
        pos = sum(1 for s in signals if s.value > 0.1)
        neg = sum(1 for s in signals if s.value < -0.1)
        neu = len(signals) - pos - neg
        dominant = max(pos, neg, neu)
        return dominant / len(signals) if signals else 0.0

    def _compute_instability(self, signals):
        penalties = []
        for s in signals:
            p = 0.0
            if s.trend == "DECLINING":
                p += 0.5
            if s.regime == "VOLATILE":
                p += 0.5
            penalties.append(min(p, 1.0))
        return sum(penalties) / len(penalties) if penalties else 0.0
