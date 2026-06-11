# aruhan/os/optimization/accuracy_booster.py

class AccuracyBooster:
    """
    Lightweight post-fusion correction layer.
    
    Improves:
    - Stress adaptation regimes
    - Inter-signal consensus amplification
    - Structural decision decisiveness under uncertainty
    """

    def adjust(self, fused, signals):
        # Gracefully handle both raw objects and JSON/Dict payloads
        if hasattr(fused, "__dict__"):
            score = getattr(fused, "score", 0.5)
            confidence = getattr(fused, "confidence", 0.5)
            instability = getattr(fused, "instability", 0.0)
            direction = getattr(fused, "direction", "NEUTRAL")
            agreement = getattr(fused, "agreement", 0.5)
        else:
            score = fused.get("score", 0.5)
            confidence = fused.get("confidence", 0.5)
            instability = fused.get("instability", 0.0)
            direction = fused.get("direction", "NEUTRAL")
            agreement = fused.get("agreement", 0.5)

        # ---------------------------------------------------------------------
        # 1. STRESS BOOST (Force decisive actions during vertical breaks)
        # ---------------------------------------------------------------------
        if instability > 0.60:
            score *= 1.15
        if instability > 0.75:
            score *= 1.30

        # ---------------------------------------------------------------------
        # 2. SIGNAL AGREEMENT BOOST (Amplify consensus, penalize noise)
        # ---------------------------------------------------------------------
        computed_agreement = self._compute_alignment(signals)

        if computed_agreement > 0.75:
            confidence *= 1.10  # Reward clear structural alignment
        elif computed_agreement < 0.40:
            confidence *= 0.80  # Heavily discount noise/disagreement

        # ---------------------------------------------------------------------
        # 3. CONSERVATIVE BOUNDARY CLAMPING
        # ---------------------------------------------------------------------
        score = max(-1.0, min(1.0, score))
        confidence = max(0.30, min(0.95, confidence))

        return {
            "score": score,
            "confidence": confidence,
            "direction": self._direction(score),
            "agreement": max(agreement, computed_agreement),
            "instability": instability
        }

    def _compute_alignment(self, signals):
        if not signals:
            return 0.0
            
        pos = sum(1 for s in signals if getattr(s, "value", 0.0) > 0.1)
        neg = sum(1 for s in signals if getattr(s, "value", 0.0) < -0.1)
        total = len(signals)

        dominant = max(pos, neg, total - pos - neg)
        return dominant / total

    def _direction(self, score):
        if score > 0.20:
            return "POSITIVE"
        elif score < -0.20:
            return "NEGATIVE"
        return "NEUTRAL"
