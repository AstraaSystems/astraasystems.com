# governance/core/ensemble_blender.py
from typing import Dict, List, Any

class EnsembleBlender:
    def __init__(self):
        # Tracking states for individual models in the ensemble
        self.estimators = {
            "kinetic_fast": {"weight": 0.40, "rolling_error": 1.0},
            "steady_state": {"weight": 0.40, "rolling_error": 1.0},
            "macro_trend":  {"weight": 0.20, "rolling_error": 1.0}
        }
        self.smoothing_factor = 0.2  # Exponential moving average for errors

    def blend_predictions(self, predictions: Dict[str, float]) -> Dict[str, Any]:
        """
        Computes a dynamically weighted average based on current model authority weights.
        """
        blended_value = 0.0
        total_weight = sum(meta["weight"] for meta in self.estimators.values())

        for name, pred_val in predictions.items():
            if name in self.estimators:
                normalized_weight = self.estimators[name]["weight"] / total_weight
                blended_value += pred_val * normalized_weight

        return {
            "blended_value": blended_value,
            "active_allocations": {k: round(v["weight"], 3) for k, v in self.estimators.items()}
        }

    def update_authority_matrix(self, predictions: Dict[str, float], actual_value: float):
        """
        Recalculates authority weights using inverse-variance scaling.
        """
        raw_inv_errors = {}
        
        for name, pred_val in predictions.items():
            if name in self.estimators:
                # Calculate absolute error for this cycle
                current_error = max(0.001, abs(pred_val - actual_value))
                
                # Smooth the error over time to prevent jittery allocation swings
                historical_err = self.estimators[name]["rolling_error"]
                updated_error = (self.smoothing_factor * current_error) + ((1 - self.smoothing_factor) * historical_err)
                self.estimators[name]["rolling_error"] = updated_error
                
                # Authority is inversely proportional to rolling error
                raw_inv_errors[name] = 1.0 / (updated_error ** 2)

        # Normalize the inverse errors to generate the new weight matrix
        sum_inv_errors = sum(raw_inv_errors.values())
        for name in self.estimators:
            self.estimators[name]["weight"] = raw_inv_errors[name] / sum_inv_errors
