# aruhan/governance/fusion/runtime.py

from .trust_engine import TrustEngine
from .fusion_engine import FusionEngine
from .decision_gate import DecisionGate


class ArkaFusionRuntime:
    """
    Upgraded Arka Governance Runtime that exposes calibration maps and
    ledger-based learning wrappers to the underlying TrustEngine.
    """
    def __init__(self, calibrators=None, adaptive_learner=None):
        # Pass the subsystems straight into the trust matrix engine
        self.trust_engine = TrustEngine(
            calibrators=calibrators,
            adaptive_learner=adaptive_learner
        )
        self.fusion_engine = FusionEngine()
        self.decision_gate = DecisionGate()

    def run(self, signals):
        for s in signals:
            s.trust_weight = self.trust_engine.compute_weight(s)

        fused = self.fusion_engine.fuse(signals)
        decision = self.decision_gate.decide(fused)

        return fused, decision, signals
