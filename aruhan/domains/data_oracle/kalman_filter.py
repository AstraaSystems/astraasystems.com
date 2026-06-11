import numpy as np

class FinancialKalmanFilter:
    def __init__(self, delta_t, process_noise_var, measurement_noise_var):
        self.delta_t = delta_t
        self.A = np.array([[1, delta_t], [0, 1]], dtype=float)
        self.H = np.array([[1, 0]], dtype=float)

        self.base_Q = np.array([
            [0.25 * (delta_t ** 4), 0.5 * (delta_t ** 3)],
            [0.5 * (delta_t ** 3),  delta_t ** 2]
        ], dtype=float) * process_noise_var

        self.Q = self.base_Q.copy()
        self.R = np.array([[measurement_noise_var]], dtype=float)
        self.P = np.eye(2, dtype=float)
        self.x = np.zeros((2, 1), dtype=float)
        self.current_q_multiplier = 1.0

    def set_q_multiplier(self, multiplier):
        self.current_q_multiplier = multiplier
        self.Q = self.base_Q * multiplier

    def predict(self):
        self.x = self.A @ self.x
        self.P = self.A @ self.P @ self.A.T + self.Q

    def correct(self, measurement):
        z = np.array([[measurement]], dtype=float)
        innovation = z - (self.H @ self.x)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.x = self.x + K @ innovation
        I = np.eye(self.P.shape[0])
        self.P = (I - K @ self.H) @ self.P
        return float(innovation[0, 0])

    def step(self, measurement):
        self.predict()
        innovation = self.correct(measurement)
        return {
            "level": float(self.x[0, 0]),
            "velocity": float(self.x[1, 0]),
            "innovation": innovation,
            "q_multiplier": float(self.current_q_multiplier)
        }
