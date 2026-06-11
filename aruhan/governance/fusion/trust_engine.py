class TrustEngine:
    def __init__(self, calibrators=None, adaptive_learner=None):
        self.calibrators = calibrators or {}
        self.adaptive_learner = adaptive_learner
        self.base_weights = {
            "dataoracle": 1.00,
            "estimator": 1.00,
            "reflection": 0.90,
            "temporal": 0.85,
        }

    def compute_weight(self, signal):
        base_weight = self.base_weights.get(signal.source, 0.5)

        # 1. Calibrated Confidence Evaluation
        calibrated_conf = signal.confidence
        reliability_from_calibration = 1.0

        calibrator = self.calibrators.get(signal.source)
        if calibrator:
            summary = calibrator.calibration_summary()
            if summary["entries"] > 20:
                reliability_from_calibration = summary["empirical_accuracy"]
                if summary["calibration_gap"] > 0.1:
                    reliability_from_calibration *= 0.75

        # 2. Ledger-Learned Reliability Factor
        learned_reliability = 1.0
        if self.adaptive_learner:
            learned_reliability = self.adaptive_learner.source_reliability(
                signal.source, current_signal=signal
            )

        # 3. Structural Signal Compounding
        weight = base_weight * calibrated_conf * reliability_from_calibration * learned_reliability

        if signal.trend == "DECLINING":
            weight *= 0.80
        elif signal.trend == "IMPROVING":
            weight *= 1.05

        if signal.regime == "VOLATILE":
            weight *= 0.85

        return max(0.0, min(weight, 1.0))
