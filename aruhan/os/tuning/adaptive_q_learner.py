from aruhan.os.memory.json_ledger import JsonLedger

class AdaptiveQLearner:
    def __init__(self):
        self.history = []

    def compute_multiplier(self, current_fusion):
        """
        Calculates the Q multiplier by comparing current fusion state
        against historical performance. Handles both dict and object inputs.
        """
        # Safely extract score
        current_score = current_fusion.get("score") if isinstance(current_fusion, dict) else getattr(current_fusion, "score", 0.0)
        
        # Default fallback
        if not self.history:
            return 1.0

        # Iterate through history to find a matching score context
        for f in self.history:
            f_score = f.get("score") if isinstance(f, dict) else getattr(f, "score", 0.0)
            
            # Logic: If we have seen a similar performance score, reuse the strategy
            if abs(f_score - current_score) < 0.2:
                # Assuming history stores a 'q_multiplier' or similar, otherwise return stable 1.0
                return f.get("q_multiplier", 1.0) if isinstance(f, dict) else getattr(f, "q_multiplier", 1.0)
        
        return 1.0        
        return 1.0 # Default fallback
        similar = []
        for r in records[-200:]:
            if "fusion" not in r:
                continue
            f = r["fusion"]
            
            # Match current spatial profile to historical logs
            if abs(f["score"] - current_fusion.score) < 0.2:
                if abs(f["instability"] - current_fusion.instability) < 0.2:
                    similar.append(r)

        if len(similar) < 5:
            return 1.0

        best_q = 1.0
        best_score = -1e9

        for r in similar:
            pred = r.get("prediction", 0.0)
            actual = r.get("measurement", 0.0)
            if actual == 0:
                continue

            score = 1.0 - abs(pred - actual)
            q = r.get("q_multiplier", 1.0)

            if score > best_score:
                best_score = score
                best_q = q

        return best_q
