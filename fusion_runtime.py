from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone

# ==========================================
# 1. CORE SIGNAL ARCHITECTURE
# ==========================================

@dataclass
class Signal:
    source: str
    signal_type: str
    value: float          # Normalized scale: [-1.0 to +1.0]
    confidence: float     # Scale: [0.0 to 1.0]
    trust_weight: float = 0.0
    trend: Optional[str] = None
    regime: Optional[str] = None
    note: Optional[str] = None

# ==========================================
# 2. GOVERNANCE & BLENDING SUBSYSTEMS
# ==========================================

class TrustEngine:
    def __init__(self):
        # Baseline prioritization vectors
        self.base_weights = {
            "dataoracle": 1.0,
            "estimator": 1.0,
            "reflection": 0.9,
            "temporal": 0.8
        }

    def compute_weight(self, signal: Signal) -> float:
        weight = self.base_weights.get(signal.source, 0.5)

        # Dynamic Penalities based on Metacognitive telemetry
        if signal.trend == "DECLINING":
            weight *= 0.80   # Reduce authority if accuracy vector is decaying
            
        if signal.regime == "VOLATILE":
            weight *= 0.85   # Apply an environmental stability discount
            
        # Linear scale factor driven by runtime confidence
        weight *= signal.confidence
        return max(0.0, min(weight, 1.0))


class FusionEngine:
    def fuse(self, signals: List[Signal]) -> dict:
        if not signals:
            return {"score": 0.0, "confidence": 0.0, "direction": "NEUTRAL"}

        weighted_sum = 0.0
        total_weight = 0.0
        confidence_sum = 0.0

        for signal in signals:
            weighted_sum += signal.value * signal.trust_weight
            total_weight += signal.trust_weight
            confidence_sum += signal.confidence * signal.trust_weight

        if total_weight == 0:
            return {"score": 0.0, "confidence": 0.0, "direction": "NEUTRAL"}

        final_score = weighted_sum / total_weight
        final_confidence = confidence_sum / total_weight

        if final_score > 0.2:
            direction = "POSITIVE"
        elif final_score < -0.2:
            direction = "NEGATIVE"
        else:
            direction = "NEUTRAL"

        return {
            "score": round(final_score, 4),
            "confidence": round(final_confidence, 4),
            "direction": direction
        }


class DecisionGate:
    def decide(self, fused_result: dict) -> dict:
        score = fused_result["score"]
        confidence = fused_result["confidence"]
        direction = fused_result["direction"]

        # Arka Sovereignty Rule: Block actions under low structural consensus
        if confidence < 0.55:
            return {"decision": "HOLD", "reason": "Ecosystem confidence matrix falls below baseline gate threshold."}

        if direction == "POSITIVE" and score > 0.5:
            return {"decision": "ACT_POSITIVE", "reason": "Strong positive alignment verified across ecosystem nodes."}

        if direction == "NEGATIVE" and score < -0.5:
            return {"decision": "ACT_DEFENSIVE", "reason": "System-wide negative variance detected. Activating defensive posture."}

        return {"decision": "MONITOR", "reason": "Signals captured within normal tolerance bands. No decisive consensus."}

# ==========================================
# 3. GLOBAL ORCHESTRATION LAYER
# ==========================================

class ArkaFusionRuntime:
    def __init__(self):
        self.trust_engine = TrustEngine()
        self.fusion_engine = FusionEngine()
        self.decision_gate = DecisionGate()

    def process_cycle(self, raw_signals: List[Signal]) -> dict:
        # Step 1: Evaluate dynamic authority metrics
        for signal in raw_signals:
            signal.trust_weight = self.trust_engine.compute_weight(signal)

        # Step 2: Blender compute via Inverse-Variance principles
        fused = self.fusion_engine.fuse(raw_signals)

        # Step 3: Run the governance decision gate
        decision = self.decision_gate.decide(fused)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "fused_telemetry": fused,
            "governance_action": decision
        }

# ==========================================
# 4. TESTING HARNESS
# ==========================================

if __name__ == "__main__":
    runtime = ArkaFusionRuntime()

    print("=========================================================================")
    print("🤖 ARKA FUSION RUNTIME: Initializing Multi-Signal Ecosystem Simulations...")
    print("=========================================================================")

    # SCENARIO 1: Structural Disagreement (Estimator says buy blindly, but the stack pushes back)
    unaligned_inputs = [
        Signal(source="estimator", signal_type="prediction", value=0.8, confidence=0.90, trend="IMPROVING", regime="VOLATILE"),
        Signal(source="dataoracle", signal_type="market", value=0.0, confidence=0.50, trend="STABLE", regime="VOLATILE"),
        Signal(source="reflection", signal_type="health", value=-0.4, confidence=0.85, trend="DECLINING", note="Model tracking lag detected"),
        Signal(source="temporal", signal_type="trend", value=-0.2, confidence=0.70, trend="DECLINING")
    ]

    print("\n🔮 Running Scenario 1: Divergent Signals (Estimator Overconfidence vs. Stack Reality)")
    result_1 = runtime.process_cycle(unaligned_inputs)
    print(f"-> Fused Score : {result_1['fused_telemetry']['score']} | Confidence: {result_1['fused_telemetry']['confidence']}")
    print(f"-> Decision    : \033[93m{result_1['governance_action']['decision']}\033[0m")
    print(f"-> Reason      : {result_1['governance_action']['reason']}")

    # SCENARIO 2: Sovereign Aligned Consensus (All units screaming the same direction)
    aligned_inputs = [
        Signal(source="estimator", signal_type="prediction", value=0.75, confidence=0.85, trend="IMPROVING", regime="NORMAL"),
        Signal(source="dataoracle", signal_type="market", value=0.65, confidence=0.80, trend="IMPROVING", regime="NORMAL"),
        Signal(source="reflection", signal_type="health", value=0.1, confidence=0.90, trend="STABLE"),
        Signal(source="temporal", signal_type="trend", value=0.4, confidence=0.85, trend="IMPROVING")
    ]

    print("\n🔥 Running Scenario 2: High-Confidence Systemic Convergence")
    result_2 = runtime.process_cycle(aligned_inputs)
    print(f"-> Fused Score : {result_2['fused_telemetry']['score']} | Confidence: {result_2['fused_telemetry']['confidence']}")
    print(f"-> Decision    : \033[92m{result_2['governance_action']['decision']}\033[0m")
    print(f"-> Reason      : {result_2['governance_action']['reason']}")
    print("=========================================================================")
