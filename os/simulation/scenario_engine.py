# os/simulation/scenario_engine.py
import copy

class ScenarioEngine:
    def __init__(self, core_math_engine):
        self.math = core_math_engine

    def stress_test_intent(self, base_intent: dict) -> dict:
        """Simulates macro-regime variations on internal state variables."""
        scenarios = ["BASELINE", "HIGH_VOLATILITY_SPIKE", "SUPPLY_CHAIN_LAG"]
        projection_manifest = {}
        
        for scenario in scenarios:
            simulated_payload = copy.deepcopy(base_intent)
            if scenario == "HIGH_VOLATILITY_SPIKE":
                simulated_payload["data"]["volatility"] = 0.95
                
            # Compute parallel reality output using the sovereign Math engine
            projection_manifest[scenario] = self.math.project(simulated_payload)
            
        return projection_manifest
