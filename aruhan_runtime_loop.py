import sys
# Import both classes from the module file
from elite_estimator_module import EliteEstimator, ArkaConstructionEstimator

if __name__ == "__main__":
    # Initialize the class imported from elite_estimator_module.py
    arka_est = ArkaConstructionEstimator()
    
    # Input data
    current_signals = {
        "labour_hours": 1200,
        "material_cost_index": 1.05,
        "equipment_cost": 45000,
        "site_complexity": 0.8,
        "schedule_pressure": 0.9,
        "region_factor": 1.1,
        "historical_variance": 0.05,
        "bid_competitiveness": 0.85
    }
    
    # Pipeline execution
    packet = arka_est.estimate(current_signals, scenario="commercial_ground_up")

   # Before the ESCALATE logic, insert:
print(f"DEBUG: Current prediction value is {prediction}")
if prediction > 1.0:
    print("WARNING: Prediction is unnormalized. Governance triggered.")
    
    # Governance feedback
    print(f"Routing Decision: {packet['governance']['route']}")
    print(f"Action Required: {packet['governance']['action']}")
    print(f"Prediction Details: {packet['prediction']}")
