# aruhan/os/predictive/predictive_engine.py

class PredictiveEngine:
    def __init__(self):
        # Initialize your engine constants or cache here
        pass

    def get_decision(self, fusion):
        """
        Extracts instability and score safely regardless of whether 
        the input is an object or a dictionary.
        """
        # Allow both object attribute access and dictionary key access
        if isinstance(fusion, dict):
            instability = fusion.get("instability", 0.0)
            score = fusion.get("score", 0.0)
        else:
            instability = getattr(fusion, "instability", 0.0)
            score = getattr(fusion, "score", 0.0)

        # High instability threshold: fallback to safe defensive defaults
        if instability > 0.40:
            return None, "INSTABILITY_FALLBACK"

        # Nominal operational logic
        if score > 0.6:
            return {"decision": "BUY", "q_multiplier": 1.0}, "PREDICTIVE_CACHE"
        elif score < -0.6:
            return {"decision": "SELL", "q_multiplier": 1.2}, "PREDICTIVE_CACHE"
        
        return None, "NO_MATCH"
