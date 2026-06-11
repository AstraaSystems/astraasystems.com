import numpy as np
from aruhan.governance.fusion.signal_models import Signal
from aruhan.os.calibration.confidence_calibrator import ConfidenceCalibrator

class EstimatorWrapper:
    def __init__(self, kf):
        self.kf = kf
        self.last_output = None
        self.last_nis = 1.0
        self.calibrator = ConfidenceCalibrator()

    def run(self, measurement):
        x_pred = self.kf.A @ self.kf.x
        P_pred = self.kf.A @ self.kf.P @ self.kf.A.T + self.kf.Q
        S = self.kf.H @ P_pred @ self.kf.H.T + self.kf.R
        
        raw_innovation = measurement - float(x_pred[0, 0])
        tracking_std = np.sqrt(S[0, 0])
        
        self.normalized_innovation = np.tanh(raw_innovation / (tracking_std + 1e-6))
        out = self.kf.step(measurement)
        self.last_nis = float((raw_innovation ** 2) / S[0, 0])
        self.last_output = out
        return out

    def build_signal(self):
        if self.last_output is None:
            return Signal(source="estimator", value=0.0, confidence=self.calibrator.calibrate(0.5), trend="STABLE")

        value = float(self.normalized_innovation)
        raw_confidence = max(0.3, min(0.95, 1.0 - (min(self.last_nis, 4.0) / 4.0)))
        calibrated_confidence = self.calibrator.calibrate(raw_confidence)

        trend = "STABLE"
        if self.last_nis > 2.0:
            trend = "DECLINING"
        elif abs(value) < 0.1:
            trend = "IMPROVING"

        regime = "VOLATILE" if self.last_nis > 3.84 else "NORMAL"
        return Signal(
            source="estimator",
            value=value,
            confidence=calibrated_confidence,
            trend=trend,
            regime=regime,
            note=f"nis={self.last_nis:.2f}, raw_conf={raw_confidence:.4f}"
        )

    def update_calibration(self, prediction, actual):
        if self.last_output is None:
            return
        raw_confidence = max(0.3, min(0.95, 1.0 - (min(self.last_nis, 4.0) / 4.0)))
        self.calibrator.update(
            raw_confidence=raw_confidence,
            prediction=prediction,
            actual=actual,
            tolerance=0.15
        )
