import numpy as np
import time
from dataclasses import dataclass
from typing import List, Optional

# ==========================================
# 1. DATA MODELS & TELEMETRY STRUCTURES
# ==========================================

@dataclass
class Signal:
    source: str
    value: float          # Scale: [-1.0 to +1.0]
    confidence: float     # Scale: [0.0 to 1.0]
    trend: str           # IMPROVING, DECLINING, STABLE
    regime: str = "NORMAL"
    trust_weight: float = 0.0

@dataclass
class FusionResult:
    score: float          # Combined system trajectory vector [-1.0 to 1.0]
    confidence: float     # Weighted system confidence matrix
    direction: str        # POSITIVE / NEGATIVE / NEUTRAL
    agreement: float      # Convergence metric [0.0 to 1.0]
    instability: float    # Tracked structural volatility [0.0 to 1.0]

# ==========================================
# 2. GOVERNANCE & BLENDING ENGINES
# ==========================================

class TrustEngine:
    def __init__(self):
        self.base_weights = {
            "dataoracle": 1.0,
            "estimator": 1.0,
            "reflection": 0.9,
            "temporal": 0.8
        }

    def compute(self, signal: Signal) -> float:
        weight = self.base_weights.get(signal.source, 0.5)
        weight *= signal.confidence
        
        if signal.trend == "DECLINING":
            weight *= 0.80
        if signal.regime == "VOLATILE":
            weight *= 0.85
            
        return max(0.0, min(weight, 1.0))


class FusionEngine:
    def fuse(self, signals: List[Signal], last_nis: float) -> FusionResult:
        if not signals:
            return FusionResult(0.0, 0.0, "NEUTRAL", 1.0, 0.0)

        weighted_sum = 0.0
        total_weight = 0.0
        confidence_sum = 0.0

        for s in signals:
            weighted_sum += s.value * s.trust_weight
            total_weight += s.trust_weight
            confidence_sum += s.confidence * s.trust_weight

        if total_weight == 0:
            return FusionResult(0.0, 0.0, "NEUTRAL", 1.0, 0.0)

        fused_score = weighted_sum / total_weight
        fused_conf = confidence_sum / total_weight

        # Compute Core Convergence Metric (Agreement)
        pos = sum(1 for s in signals if s.value > 0.1)
        neg = sum(1 for s in signals if s.value < -0.1)
        neu = len(signals) - pos - neg
        agreement = max(pos, neg, neu) / len(signals)

        # Compute Ecosystem Instability + Inject Kalman Innovation Feedback Loop
        penalties = []
        for s in signals:
            p = 0.0
            if s.trend == "DECLINING": p += 0.4
            if s.regime == "VOLATILE": p += 0.4
            penalties.append(min(p, 1.0))
        
        base_instability = sum(penalties) / len(penalties) if penalties else 0.0
        
        # Cybernetic loop: High Normalized Innovation Squared (NIS > 2.0) spikes system instability
        nis_penalty = min(1.0, max(0.0, (last_nis - 1.0) / 4.0))
        instability = max(base_instability, nis_penalty)

        if fused_score > 0.2:
            direction = "POSITIVE"
        elif fused_score < -0.2:
            direction = "NEGATIVE"
        else:
            direction = "NEUTRAL"

        return FusionResult(
            score=round(fused_score, 4),
            confidence=round(fused_conf, 4),
            direction=direction,
            agreement=round(agreement, 2),
            instability=round(instability, 4)
        )


class DecisionGate:
    def decide(self, fusion: FusionResult) -> dict:
        if fusion.confidence < 0.55:
            return {"action": "HOLD", "reason": "System consensus matrix degraded below execution floor."}
        if fusion.direction == "POSITIVE" and fusion.score > 0.40:
            return {"action": "ACT_POSITIVE", "reason": "Unified positive vector verified."}
        if fusion.direction == "NEGATIVE" and fusion.score < -0.40:
            return {"action": "ACT_DEFENSIVE", "reason": "System-wide downward variance detected."}
        return {"action": "MONITOR", "reason": "Ecosystem idling within balanced variance channels."}

# ==========================================
# 3. ADAPTIVE PARAMETER ACTUATOR
# ==========================================

class QTuningPolicy:
    def __init__(self, min_multiplier: float = 0.5, max_multiplier: float = 3.5):
        self.min_multiplier = min_multiplier
        self.max_multiplier = max_multiplier

    def compute_multiplier(self, fusion: FusionResult, reflection_flag: str, temporal_trend: str) -> float:
        multiplier = 1.0

        # Scale process uncertainty based on ecosystem mapping
        multiplier += 1.0 * fusion.instability
        multiplier += 0.6 * (1.0 - fusion.agreement)

        if reflection_flag == "HIGH_ERROR":
            multiplier += 0.5
        if temporal_trend == "DECLINING":
            multiplier += 0.3

        # Settle parameters if system tracks cleanly and uniformly
        if fusion.confidence > 0.8 and fusion.agreement > 0.8 and fusion.instability < 0.15:
            multiplier -= 0.25

        return max(self.min_multiplier, min(multiplier, self.max_multiplier))

# ==========================================
# 4. FINANCIAL KALMAN FILTER INFRASTRUCTURE
# ==========================================

class FinancialKalmanFilter:
    def __init__(self, delta_t: float, process_noise_var: float, measurement_noise_var: float):
        self.delta_t = delta_t
        self.A = np.array([[1.0, delta_t], [0.0, 1.0]])
        self.H = np.array([[1.0, 0.0]])
        
        # Static baseline parameters to anchor state trajectory and prevent system drift
        self.base_Q = np.array([
            [0.25 * (delta_t ** 4), 0.5 * (delta_t ** 3)],
            [0.5 * (delta_t ** 3),  delta_t ** 2]
        ]) * process_noise_var

        self.Q = self.base_Q.copy()
        self.R = np.array([[measurement_noise_var]])
        self.P = np.eye(2) * 1.0
        self.x = np.zeros((2, 1))
        self.last_nis = 1.0

    def adapt_process_noise(self, multiplier: float):
        self.Q = self.base_Q * multiplier

    def cycle(self, measurement: float) -> float:
        # Time Update (Predict)
        self.x = self.A @ self.x
        self.P = self.A @ self.P @ self.A.T + self.Q

        # Measurement Update (Correct)
        z = np.array([[measurement]])
        innovation = z - (self.H @ self.x)
        
        # Compute Innovation Covariance S and Normalized Innovation Squared (NIS)
        S = self.H @ self.P @ self.H.T + self.R
        S_inv = 1.0 / S[0, 0]
        
        self.last_nis = float((innovation[0, 0] ** 2) * S_inv)

        # Apply Kalman Gain
        K = self.P @ self.H.T * S_inv
        self.x = self.x + K * innovation
        self.P = (np.eye(2) - K @ self.H) @ self.P

        return self.last_nis

# ==========================================
# 5. CYBERNETIC CLOSED-LOOP ORCHESTRATOR (DYNAMIC SYSTEM)
# ==========================================

class CyberneticGovernor:
    def __init__(self):
        self.kf = FinancialKalmanFilter(delta_t=1.0, process_noise_var=0.05, measurement_noise_var=0.20)
        self.trust_engine = TrustEngine()
        self.fusion_engine = FusionEngine()
        self.decision_gate = DecisionGate()
        self.q_policy = QTuningPolicy()

    def run_tick(self, measurement: float, dataoracle_val: float, market_regime: str, 
                 reflection_flag: str, temporal_trend: str) -> dict:
        
        # 1. Peek at the system's prior state to calculate the upcoming prediction error
        x_pred = self.kf.A @ self.kf.x
        P_pred = self.kf.A @ self.kf.P @ self.kf.A.T + self.kf.Q
        S = self.kf.H @ P_pred @ self.kf.H.T + self.kf.R
        
        # 2. Compute Raw Innovation and Standard Deviation of the tracking system
        raw_innovation = measurement - float(x_pred[0, 0])
        tracking_std = np.sqrt(S[0, 0])
        
        # 3. Dynamic Delta Normalization: Scale the signal by its mathematical standard deviation
        # Soft-bound it to [-1.0, 1.0] using a hyperbolic tangent to fit Arka's input layer
        normalized_innovation_signal = np.tanh(raw_innovation / (tracking_std + 1e-6))

        # 4. Wrap environmental context into active telemetry signals
        estimator_signal = Signal(
            source="estimator", 
            value=float(normalized_innovation_signal), 
            confidence=0.85, 
            trend="STABLE" if self.kf.last_nis < 2.0 else "DECLINING"
        )
        dataoracle_signal = Signal(source="dataoracle", value=dataoracle_val, confidence=0.80, trend=temporal_trend, regime=market_regime)
        reflection_signal = Signal(source="reflection", value=-0.3 if reflection_flag == "LOW_ERROR" else -0.7, confidence=0.75, trend=temporal_trend)
        temporal_signal = Signal(source="temporal", value=dataoracle_val * 0.9, confidence=0.70, trend=temporal_trend)

        signals = [estimator_signal, dataoracle_signal, reflection_signal, temporal_signal]

        # 5. Compute Dynamic Trust Metrics
        for s in signals:
            s.trust_weight = self.trust_engine.compute(s)

        # 6. Global System Fusion with injected tracking NIS feedback
        fusion_result = self.fusion_engine.fuse(signals, self.kf.last_nis)

        # 7. Actuate Adaptive Parameter Control Law
        q_multiplier = self.q_policy.compute_multiplier(fusion_result, reflection_flag, temporal_trend)
        self.kf.adapt_process_noise(q_multiplier)

        # 8. Execute State Space Kinematics
        nis = self.kf.cycle(measurement)
        decision = self.decision_gate.decide(fusion_result)

        return {
            "state_estimate": round(float(self.kf.x[0, 0]), 2),
            "velocity_estimate": round(float(self.kf.x[1, 0]), 4),
            "nis_telemetry": round(nis, 4),
            "q_multiplier": round(q_multiplier, 2),
            "fusion_score": round(fusion_result.score, 4),
            "governance_decision": decision
        }

# ==========================================
# 6. CLOSED-LOOP STRESS TEST TIMELINE
# ==========================================

if __name__ == "__main__":
    governor = CyberneticGovernor()
    governor.kf.x[0, 0] = 100.0

    print("=========================================================================")
    print("🔄 INITIALIZING CALIBRATED ARKA CYBERNETIC SIMULATION")
    print("=========================================================================")

    timeline = [
        {"measurement": 101.0, "oracle": 0.05, "regime": "NORMAL", "reflect": "LOW_ERROR", "trend": "STABLE"},
        {"measurement": 102.1, "oracle": 0.08, "regime": "NORMAL", "reflect": "LOW_ERROR", "trend": "STABLE"},
        # --- TICK 3: STRUCTURAL REGIME BREAK ---
        {"measurement": 92.5, "oracle": -0.65, "regime": "VOLATILE", "reflect": "HIGH_ERROR", "trend": "DECLINING"},
        {"measurement": 89.0, "oracle": -0.50, "regime": "VOLATILE", "reflect": "MEDIUM_ERROR", "trend": "DECLINING"},
        {"measurement": 88.2, "oracle": -0.10, "regime": "NORMAL", "reflect": "LOW_ERROR", "trend": "STABLE"},
    ]

    for idx, tick in enumerate(timeline):
        res = governor.run_tick(
            measurement=tick["measurement"],
            dataoracle_val=tick["oracle"],
            market_regime=tick["regime"],
            reflection_flag=tick["reflect"],
            temporal_trend=tick["trend"]
        )
        print(f"\n⏱️ [TICK {idx + 1}] Target Input: {tick['measurement']}")
        print(f"   └─ Tracked State : {res['state_estimate']} (Velocity: {res['velocity_estimate']})")
        print(f"   └─ Fusion Score  : {res['fusion_score']}")
        print(f"   └─ Q Multiplier  : \033[94m{res['q_multiplier']}x\033[0m Window")
        print(f"   └─ Arka Gate     : \033[91m{res['governance_decision']['action']}\033[0m -> {res['governance_decision']['reason']}")
    print("=========================================================================")
