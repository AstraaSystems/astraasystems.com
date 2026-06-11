class ConfidenceCalibrator:
    """
    Simple online confidence calibrator that records predictions vs outcomes
    to systematically prevent overconfidence.
    """
    def __init__(self, max_history=500):
        self.history = []
        self.max_history = max_history

    def update(self, raw_confidence: float, prediction: float, actual: float, tolerance: float = 0.10):
        error = abs(prediction - actual)
        correct = 1 if error <= tolerance else 0

        self.history.append({
            "raw_confidence": max(0.0, min(1.0, raw_confidence)),
            "correct": correct,
            "error": error
        })

        if len(self.history) > self.max_history:
            self.history.pop(0)

    def calibrate(self, raw_confidence: float):
        raw_confidence = max(0.0, min(1.0, raw_confidence))
        if len(self.history) < 20:
            return raw_confidence

        window = 0.10
        nearby = [h for h in self.history if abs(h["raw_confidence"] - raw_confidence) <= window]

        if len(nearby) < 5:
            return raw_confidence

        empirical_accuracy = sum(h["correct"] for h in nearby) / len(nearby)
        
        # Blend raw heuristics with empirical reality
        calibrated = 0.5 * raw_confidence + 0.5 * empirical_accuracy
        return max(0.0, min(1.0, calibrated))

    def calibration_summary(self):
        if not self.history:
            return {"entries": 0, "avg_raw_confidence": 0.0, "empirical_accuracy": 0.0, "calibration_gap": 0.0}

        avg_raw = sum(h["raw_confidence"] for h in self.history) / len(self.history)
        empirical = sum(h["correct"] for h in self.history) / len(self.history)
        gap = avg_raw - empirical

        return {
            "entries": len(self.history),
            "avg_raw_confidence": round(avg_raw, 4),
            "empirical_accuracy": round(empirical, 4),
            "calibration_gap": round(gap, 4)
        }
