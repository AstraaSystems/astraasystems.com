import json
import os
import datetime
from typing import Dict, Any

LEDGER_PATH = "reflection_ledger.json"

class MetacognitiveCore:
    def __init__(self):
        self.baseline_confidence = 1.0

    def calculate_temporal_multiplier(self, window_size: int = 5) -> float:
        """
        Looks back through the historical reflection ledger to evaluate recent consistency.
        Returns a time-weighted scaling modifier based on trailing performance.
        """
        if not os.path.exists(LEDGER_PATH):
            return 1.0  # Zero historical data context, maintain neutral weight
            
        try:
            with open(LEDGER_PATH, "r") as f:
                ledger = json.load(f)
        except Exception:
            return 1.0

        if not ledger:
            return 1.0

        # Extract the trailing N historical runs
        recent_history = ledger[-window_size:]
        lag_events = 0
        total_records = len(recent_history)

        for record in recent_history:
            status = record.get("evaluation", {}).get("regime_status", "STABLE")
            if status == "HIGH_SYSTEM_LAG_DETECTED":
                lag_events += 1

        # Temporal Penalty Mechanics: ongoing instability aggressively decays historical confidence
        if total_records > 0:
            error_ratio = lag_events / total_records
            # Scale down the modifier as systematic errors compound over time
            temporal_modifier = 1.0 - (error_ratio * 0.3)
            return max(0.4, round(temporal_modifier, 4))
            
        return 1.0

    def evaluate_lifecycle(self, initial_intent: dict, execution_output: dict) -> Dict[str, Any]:
        """
        Analyzes deviations between math estimations and real-world domain behaviors 
        while incorporating time-weighted historical memory coefficients.
        """
        returned_state = execution_output.get("returned_state", {})
        analytical_truth = returned_state.get("analytical_truth", {})
        state_estimation = analytical_truth.get("state_estimation", {})
        real_world_action = returned_state.get("real_world_action", {})
        
        velocity = state_estimation.get("velocity", 0.0)
        volatility = initial_intent.get("data", {}).get("volatility", 0.0)
        projected_demand = real_world_action.get("arkastra_commerce", {}).get("projected_demand_factor", 0.0)
        
        # Calculate structural deviation
        expected_equilibence = velocity * (1.0 - volatility)
        system_tension = abs(projected_demand - expected_equilibence)
        
        # 1. Compute current step modifications
        deviation_status = "STABLE"
        confidence_delta = 0.01
        
        if system_tension > 50.0:
            deviation_status = "HIGH_SYSTEM_LAG_DETECTED"
            confidence_delta = -0.05
            reflection_note = "Kalman regime variance multiplier under-indexed relative to input volatility spikes."
        elif system_tension > 10.0:
            deviation_status = "MODERATE_DRIFT"
            confidence_delta = -0.02
            reflection_note = "Minor variance tracking latency observed in distribution efficiency vectors."
        else:
            reflection_note = "Mathematical truth metrics and real-world actions are perfectly aligned."

        # Apply short-term confidence shift
        self.baseline_confidence = max(0.1, min(1.0, self.baseline_confidence + confidence_delta))
        
        # 2. Extract Temporal Context Matrix
        temporal_multiplier = self.calculate_temporal_multiplier(window_size=5)
        
        # 3. Formulate the Absolute Compound Confidence Vector
        compound_signal_confidence = max(0.05, round(self.baseline_confidence * temporal_multiplier, 4))
        
        reflection_profile = {
            "timestamp": f"{datetime.datetime.utcnow().isoformat()}Z",
            "task_action": initial_intent.get("action", "STATE_AUDIT"),
            "metrics_evaluated": {
                "input_volatility": volatility,
                "estimated_velocity": round(velocity, 4),
                "calculated_system_tension": round(system_tension, 4)
            },
            "temporal_intelligence": {
                "trailing_memory_multiplier": temporal_multiplier,
                "compound_signal_confidence": compound_signal_confidence
            },
            "evaluation": {
                "regime_status": deviation_status,
                "updated_system_confidence": round(self.baseline_confidence, 4),
                "remedial_action": reflection_note
            }
        }
        
        self._commit_to_ledger(reflection_profile)
        return reflection_profile

    def _commit_to_ledger(self, profile: dict):
        ledger_data = []
        if os.path.exists(LEDGER_PATH):
            try:
                with open(LEDGER_PATH, "r") as f:
                    ledger_data = json.load(f)
            except Exception:
                ledger_data = []
                
        ledger_data.append(profile)
        with open(LEDGER_PATH, "w") as f:
            json.dump(ledger_data, indent=2, fp=f)
