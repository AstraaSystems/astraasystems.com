import numpy as np
from typing import Dict, Any

class FinancialKalmanFilter:
    def __init__(self, delta_t: float = 1.0, process_noise_var: float = 0.01, measurement_noise_var: float = 0.05):
        self.delta_t = delta_t
        self.A = np.array([[1.0, delta_t], [0.0, 1.0]], dtype=float)
        self.H = np.array([[1.0, 0.0]], dtype=float)
        self.base_Q = np.array([
            [0.25 * (delta_t**4), 0.5 * (delta_t**3)],
            [0.5 * (delta_t**3), delta_t**2]
        ], dtype=float) * process_noise_var
        self.Q = self.base_Q.copy()
        self.R = np.array([[measurement_noise_var]], dtype=float)
        self.x = np.zeros((2, 1), dtype=float)
        self.P = np.eye(2, dtype=float) * 1.0

    def update_tracking_regime(self, yield_spread_volatility: float) -> None:
        multiplier = 1.0 + max(0.0, yield_spread_volatility)
        self.Q = self.base_Q * multiplier

    def run(self, inputs: dict) -> Dict[str, Any]:
        measurement = inputs["measurement"]
        volatility = inputs["yield_spread_volatility"]
        self.update_tracking_regime(volatility)
        self.x = self.A @ self.x
        self.P = self.A @ self.P @ self.A.T + self.Q
        z = np.array([[measurement]], dtype=float)
        y = z - (self.H @ self.x)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        I = np.eye(self.P.shape[0], dtype=float)
        self.P = (I - K @ self.H) @ self.P
        return {
            "level": float(self.x[0, 0]),
            "velocity": float(self.x[1, 0]),
            "covariance": self.P.tolist()
        }
