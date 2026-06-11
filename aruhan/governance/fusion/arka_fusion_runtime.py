from typing import List
from datetime import datetime, timezone
from .signal_models import Signal
from .trust_engine import TrustEngine
from .fusion_engine import FusionEngine
from .decision_gate import DecisionGate
from .dissonance_governor import DissonanceGovernor  # <-- ADD THIS IMPORT

class ArkaFusionRuntime:
    def __init__(self, current_kalman_q: float = 0.5):
        self.trust_engine = TrustEngine()
        self.fusion_engine = FusionEngine()
        self.decision_gate = DecisionGate()
        self.governor = DissonanceGovernor(sensitivity_alpha=2.0) # <-- INITIALIZE
        self.kalman_q = current_kalman_q

    def process_cycle(self, raw_signals: List[Signal]) -> dict:
        for signal in raw_signals:
            signal.trust_weight = self.trust_engine.compute_weight(signal)

        fused = self.fusion_engine.fuse(raw_signals)
        decision = self.decision_gate.decide(fused)

        # <-- RUN THE CLOSED-LOOP TUNING HOOK HERE -->
        optimized_q, delta_variance, strategy = self.governor.evaluate_and_tune(
            signals=raw_signals,
            fused_result=fused,
            current_q=self.kalman_q
        )
        self.kalman_q = optimized_q  # Store the mutated Q for the next cycle

        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "fused_telemetry": fused,
            "governance_action": decision,
            "cybernetic_tuning": {
                "optimized_q": optimized_q,
                "disagreement_delta": delta_variance,
                "strategy": strategy
            }
        }
