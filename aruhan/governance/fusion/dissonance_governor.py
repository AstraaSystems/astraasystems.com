# ====== DISSONANCE GOVERNOR (The Feedback Hook) ======

class DissonanceGovernor:
    def __init__(self, sensitivity_alpha: float = 1.5):
        self.alpha = sensitivity_alpha

    def evaluate_and_tune(self, signals: list, fused_result: dict, current_q: float) -> tuple:
        """
        Measures how far the mathematical estimator has drifted from the collective ecosystem mind,
        and derives an optimized parameter correction factor for the Kalman filter.
        """
        fused_score = fused_result["score"]
        
        # Extract the live estimator value from the active signal registry
        estimator_signal = next((s for s in signals if s.source == "estimator"), None)
        if not estimator_signal:
            return current_q, 0.0

        # Calculate absolute variance from consensus (Systemic Disagreement)
        disagreement = abs(estimator_signal.value - fused_score)

        # Actuation Logic:
        # High Disagreement means the model is out of sync with reality -> Scale up Q to increase flexibility.
        # Low Disagreement means the model is aligned -> Slowly damp Q to lock in steady-state stability.
        if disagreement > 0.35:
            # Scale Q aggressively using a linear feedback modifier
            q_modifier = 1.0 + (disagreement * self.alpha)
            new_q = current_q * q_modifier
            action_taken = "SCALE_UP_FLEXIBILITY"
        else:
            new_q = current_q * 0.95
            action_taken = "STABILIZE_REGIME"

        # Structural safety boundaries to prevent mathematical explosions
        new_q = max(0.01, min(new_q, 5.0))

        return new_q, disagreement, action_taken


# ====== CONNECTING TO YOUR INTEGRATED RUNTIME ======

def run_cybernetic_cycle(current_kalman_q: float):
    # 1. Gather your unified ecosystem inputs
    signals = build_signals()
    
    # 2. Run your existing Trust and Fusion blocks
    trust_engine = TrustEngine()
    fusion_engine = FusionEngine()
    
    for s in signals:
        s.trust_weight = trust_engine.compute(s)
        
    fused = fusion_engine.fuse(signals)
    
    # 3. Invoke the Dissonance Governor
    governor = DissonanceGovernor(sensitivity_alpha=2.0)
    optimized_q, delta_variance, strategy = governor.evaluate_and_tune(
        signals=signals, 
        fused_result=fused, 
        current_q=current_kalman_q
    )
    
    print("\n=== CYBERNETIC FEEDBACK METRICS ===")
    print(f"-> System Consensus Score : {fused['score']:.4f}")
    print(f"-> Estimator Disagreement : {delta_variance:.4f}")
    print(f"-> Governance Strategy    :  {strategy}")
    print(f"-> Parameter Mutation     : Kalman Q shifted from {current_kalman_q:.4f} ──> {optimized_q:.4f}")
    
    return optimized_q

# Execute a tracking tick
next_cycle_q = run_cybernetic_cycle(current_kalman_q=0.50)
