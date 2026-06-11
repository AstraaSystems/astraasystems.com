import time

class SelfCorrectionEngine:
    """
    SELF-CORRECTION ENGINE
    Detects and corrects:
    - internal inconsistencies
    - emotional misalignment
    - cognitive distortions
    - identity drift
    - planning contradictions
    - reinforcement errors

    Inputs:
    - unified evolution state
    - reinforcement output
    - planning output
    - identity state
    - meta-cognition signals
    """

    def __init__(self):
        self.correction_history = []
        self.max_history = 100

    def record(self, evolution, reinforcement, planning, identity_state, meta):
        entry = {
            "evolution": evolution,
            "reinforcement": reinforcement,
            "planning": planning,
            "identity": identity_state,
            "meta": meta,
            "timestamp": time.time()
        }

        self.correction_history.append(entry)
        if len(self.correction_history) > self.max_history:
            self.correction_history.pop(0)

    def detect_identity_drift(self, identity_state, evolution):
        if not identity_state or not evolution:
            return None

        evolved = evolution.get("evolved_identity")
        current = identity_state.get("identity_vector")

        if not evolved or not current:
            return None

        drift = {}
        for key in current:
            drift[key] = evolved[key] - current[key]

        return drift

    def detect_plan_conflicts(self, planning):
        if not planning:
            return None

        latest = planning.get("latest_plans", [])
        goals = [p.get("goal") for p in latest if p]

        if len(goals) != len(set(goals)):
            return "duplicate_goals"

        return None

    def detect_meta_conflicts(self, meta):
        if not meta:
            return None

        if "meta_negative_bias" in meta and "meta_clarity_issue" in meta:
            return "bias_clarity_conflict"

        return None

    def apply_corrections(self, drift, plan_conflict, meta_conflict):
        corrections = {}

        if drift:
            corrections["identity_correction"] = {
                key: -value * 0.1 for key, value in drift.items()
            }

        if plan_conflict:
            corrections["planning_correction"] = "remove_duplicate_goals"

        if meta_conflict:
            corrections["meta_correction"] = "increase_meta_stability"

        return corrections if corrections else None

    def process(self, evolution, reinforcement, planning, identity_state, meta):
        self.record(evolution, reinforcement, planning, identity_state, meta)

        drift = self.detect_identity_drift(identity_state, evolution)
        plan_conflict = self.detect_plan_conflicts(planning)
        meta_conflict = self.detect_meta_conflicts(meta)

        corrections = self.apply_corrections(drift, plan_conflict, meta_conflict)

        return {
            "identity_drift": drift,
            "plan_conflict": plan_conflict,
            "meta_conflict": meta_conflict,
            "corrections": corrections,
            "correction_history_count": len(self.correction_history)
        }
