import math
import random
from pathlib import Path

# Core Domain Engines
from aruhan.domains.data_oracle.kalman_filter import FinancialKalmanFilter
from aruhan.domains.data_oracle.estimator_wrapper import EstimatorWrapper
from aruhan.domains.data_oracle.dataoracle import DataOracle

# OS & Governance Modules
from aruhan.os.reflection.reflection_engine import ReflectionEngine
from aruhan.os.temporal.temporal_engine import TemporalEngine
from aruhan.os.tuning.adaptive_q_learner import AdaptiveQLearner
from aruhan.os.memory.json_ledger import JsonLedger
from aruhan.os.predictive.predictive_engine import PredictiveEngine
from aruhan.os.optimization.accuracy_booster import AccuracyBooster
from aruhan.os.optimization.stability_gate import StabilityGate

# Governance Fusion
from aruhan.governance.fusion.adaptive_trust_learner import AdaptiveTrustLearner
from aruhan.governance.fusion.runtime import ArkaFusionRuntime


# Update the generator signature in main.py
def synthetic_market_series(n=500, seed=7):
    random.seed(seed)
    series = []
    x = 100.0
    for t in range(n):
        trend = 0.03 * t / n
        wave = 0.15 * math.sin(t / 3.0)
        
        # We keep the original crash at 15 for consistency,
        # but the engine will now have 485 cycles to recover and stabilize.
        if t == 15:
            x -= 12.0
        elif t > 15:
            noise = random.uniform(-0.50, -0.10)
        else:
            noise = random.uniform(-0.05, 0.05)
            
        x = x + trend + wave + noise
        series.append(round(x, 4))
    return series

def compute_accuracy_like(prediction, actual):
    error = abs(prediction - actual)
    return max(0.0, 1.0 - error)


def main():
    print("=========================================================================")
    print("🔄 INITIALIZING AUTONOMOUS ADAPTIVE GOVERNED ENGINE (ARUHAN ENGINE)")
    print("=========================================================================")

    measurements = synthetic_market_series(n=500)

    kf = FinancialKalmanFilter(delta_t=1.0, process_noise_var=0.05, measurement_noise_var=0.20)
    kf.x[0, 0] = 100.0

    estimator = EstimatorWrapper(kf)
    reflection = ReflectionEngine()
    temporal = TemporalEngine()
    dataoracle = DataOracle()
    
    ledger = JsonLedger()
    ledger.path = Path("aruhan_ledger.jsonl")

    adaptive_trust = AdaptiveTrustLearner()
    q_learner = AdaptiveQLearner()
    predictive_engine = PredictiveEngine()
    booster = AccuracyBooster()
    stability_gate = StabilityGate(threshold=3)

    calibrators = {"estimator": estimator.calibrator}
    fusion_runtime = ArkaFusionRuntime(calibrators=calibrators, adaptive_learner=adaptive_trust)

    recent_measurements = []
    shock_intensity = 0.0

    for i, actual_measurement in enumerate(measurements):
        recent_measurements.append(actual_measurement)

        # PASS 1: Pre-flight Fusion
        data_signal = dataoracle.build_signal(actual_measurement, recent_measurements)
        reflection_signal = reflection.latest_error_signal()
        temporal_signal = temporal.temporal_signal()
        estimator_signal_pre = estimator.build_signal()
        
        pre_signals = [data_signal, estimator_signal_pre, reflection_signal, temporal_signal]
        fused_pre, pre_decision, weighted_signals = fusion_runtime.run(pre_signals)

        # Breach detection using raw fusion output
        # Using .get() ensures we don't hit AttributeErrors if fusion is a dict
        instability = fused_pre.get("instability", 0.0) if isinstance(fused_pre, dict) else getattr(fused_pre, "instability", 0.0)
        raw_innovation = actual_measurement - kf.x[0, 0]
        
        is_breached = abs(raw_innovation) > 3.0 or instability > 0.40
        is_validated_crash = stability_gate.validate(is_breached)

        # Boosted Accuracy Adjustment
        fused_adjusted = booster.adjust(fused_pre, weighted_signals)

        # Hysteresis Quenching Logic
        if is_breached:
            shock_intensity = 1.0
        else:
            shock_intensity *= 0.40 if abs(raw_innovation) < 0.20 else 0.75

        # Decision Matrix
        q_multiplier = 1.0
        prediction_source = "LIVE_COMPUTE"
        decision = pre_decision

        if shock_intensity > 0.15:
            prediction_source = "SHOCK_ESCAPE_HATCH"
            decision = "ACT DEFENSIVE"
            q_multiplier = 1.0 + (2.5000 * shock_intensity)
            
            # State injection only if crash is validated
            if is_validated_crash:
                kf.x[0, 0] = actual_measurement
                kf.x[1, 0] = 0.0
        else:
            predicted_policy, source_flag = predictive_engine.get_decision(fused_adjusted)
            if predicted_policy:
                decision = predicted_policy["decision"]
                q_multiplier = predicted_policy["q_multiplier"]
                prediction_source = source_flag
            else:
                prediction_source = "LEDGER_MINING"
                q_multiplier = q_learner.compute_multiplier(fused_adjusted)
                if q_multiplier < 0.7 or q_multiplier > 2.5:
                    q_multiplier = 1.0

        kf.set_q_multiplier(q_multiplier)

        # PASS 2: Execution
        est_output = estimator.run(actual_measurement)
        prediction = est_output["level"]
        
        reflection_flag, _ = reflection.reflect(prediction, actual_measurement, estimator.build_signal().confidence)
        estimator.update_calibration(prediction, actual_measurement)
        temporal.update(compute_accuracy_like(prediction, actual_measurement))

        print(f"\n⏱️ [CYCLE {i+1:02d}] Target: {actual_measurement:.2f} -> Estimate: {prediction:.2f}")
        print(f"   ├─ Arka Gate     : {decision:<13} [Source: {prediction_source}]")
        print(f"   └─ Applied Q     : {q_multiplier:.4f}x")

        ledger.append({
            "cycle": i + 1,
            "measurement": actual_measurement,
            "prediction": prediction,
            "fusion": fused_adjusted,
            "decision": decision,
            "prediction_source": prediction_source,
            "signals": [{"source": s.source, "value": s.value, "confidence": s.confidence} for s in weighted_signals]
        })

    print(f"\n💾 LEDGER RECORD COMMITTED TO: {ledger.path}")

if __name__ == "__main__":
    main()
