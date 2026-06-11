# governance/meta/decision_memory.py
class DecisionMemory:
    def __init__(self):
        self.global_decision_ledger = []

    def verify_tactical_consistency(self, proposed_action: str, current_posture: str) -> bool:
        """Audits strategic continuity to flag contradictory internal behavioral shifts."""
        if not self.global_decision_ledger:
            return True
            
        last_strategic_posture = self.global_decision_ledger[-1].get("posture")
        if last_strategic_posture == "DEFENSIVE" and proposed_action == "AGGRESSIVE_EXPOSURE":
            return False  # Structural tension detected: Flags Arka for review
        return True
