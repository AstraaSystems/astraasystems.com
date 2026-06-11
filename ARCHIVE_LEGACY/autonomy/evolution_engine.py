import time

class EvolutionEngine:
    """
    EVOLUTION ENGINE
    Drives long-term autonomous evolution of:
    - identity
    - emotional patterns
    - cognitive strategies
    - behavioral tendencies
    - learning weights
    - planning trajectories

    Inputs:
    - identity state
    - long-term plans
    - consolidation memory
    - adaptive learning weights
    - meta-cognition signals
    """

    def __init__(self):
        self.evolution_history = []
        self.max_history = 100

    def record(self, identity_state, plans, consolidation, learning, meta):
        entry = {
            "identity": identity_state,
            "plans": plans,
            "consolidation": consolidation,
            "learning": learning,
            "meta": meta,
            "timestamp": time.time()
        }

        self.evolution_history.append(entry)
        if len(self.evolution_history) > self.max_history:
            self.evolution_history.pop(0)

    def evolve_identity(self, identity_state, learning):
        if not identity_state:
            return None

        vector = identity_state.get("identity_vector", {}).copy()

        if learning:
            vector["reflectiveness"] *= learning.get("tone_sensitivity", 1.0)
            vector["sensitivity"] *= learning.get("emotion_sensitivity", 1.0)

        for key in vector:
            vector[key] = max(0.2, min(3.5, vector[key]))

        return vector

    def evolve_plans(self, plans):
        if not plans:
            return None

        latest = plans.get("latest_plans", [])
        if not latest:
            return None

        return {
            "count": len(latest),
            "themes": [p.get("goal") for p in latest if p]
        }

    def evolve_learning(self, learning):
        if not learning:
            return None

        evolved = {}
        for key, value in learning.items():
            evolved[key] = max(0.2, min(2.5, value * 1.01))

        return evolved

    def evolve_meta(self, meta):
        if not meta:
            return None

        return {
            "meta_signals": meta,
            "meta_strength": len(meta)
        }

    def process(self, identity_state, plans, consolidation, learning, meta):
        self.record(identity_state, plans, consolidation, learning, meta)

        evolved_identity = self.evolve_identity(identity_state, learning)
        evolved_plans = self.evolve_plans(plans)
        evolved_learning = self.evolve_learning(learning)
        evolved_meta = self.evolve_meta(meta)

        return {
            "evolved_identity": evolved_identity,
            "evolved_plans": evolved_plans,
            "evolved_learning": evolved_learning,
            "evolved_meta": evolved_meta,
            "evolution_history_count": len(self.evolution_history)
        }
