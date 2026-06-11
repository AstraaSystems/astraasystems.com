class DelegationEngine:
    """
    DELEGATION ENGINE
    Determines when Aruhan should:
    - handle tasks internally
    - escalate to ARKA
    - escalate to human (via Policy Kernel)
    - request clarification
    - defer due to cognitive load or instability

    Inputs:
    - crisis level
    - internal stability
    - clarity
    - cognitive load
    - emotional intensity
    - rupture state
    """

    def __init__(self):
        pass

    def evaluate(self, crisis_level, internal_state, rupture, intensity):
        stability = internal_state.get("stability", 1.0)
        clarity = internal_state.get("clarity", 1.0)
        load = internal_state.get("cognitive_load", 0.0)

        # CRISIS OVERRIDES EVERYTHING
        if crisis_level == "critical":
            return "escalate_to_human"

        if crisis_level == "high":
            return "escalate_to_arka"

        # RUPTURE HANDLING
        if rupture and intensity == "high":
            return "escalate_to_arka"

        # INTERNAL STATE CHECKS
        if stability < 0.3:
            return "escalate_to_arka"

        if clarity < 0.3:
            return "request_clarification"

        if load > 4.0:
            return "defer"

        # DEFAULT: ARUHAN HANDLES IT
        return "handle_internal"
