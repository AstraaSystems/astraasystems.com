import json
import time
from governance.core.approval_gate import ArkaGovernor
from app.core.reflection_engine import MetacognitiveCore

if __name__ == "__main__":
    governor = ArkaGovernor()
    reflection_engine = MetacognitiveCore()
    
    print("\n==================== INITIATING MULTI-CYCLE TEMPORAL RUNS ====================")
    
    user_command_payload = {
        "origin": "arka_internal_secure",
        "target_domain": "vsv_ai",
        "action": "SIMULATE_VALUE_FLOW",
        "data": {
            "price": 108.75,
            "volatility": 0.65
        }
    }
    
    # Simulate an active temporal series of executions
    for run_id in range(1, 4):
        print(f"\n⚡ Executing Tactical Lifecycle Pass #{run_id}...")
        
        response_payload = governor.route_to_kernel(user_command_payload)
        reflection_assessment = reflection_engine.evaluate_lifecycle(user_command_payload, response_payload)
        
        print(f"📌 [Memory Trace]: Trailing Multiplier: {reflection_assessment['temporal_intelligence']['trailing_memory_multiplier']} | Compound Confidence: {reflection_assessment['temporal_intelligence']['compound_signal_confidence']}")
        time.sleep(0.5)

    print("\n===============================================================================")
    print("💾 [SYSTEM]: Execution train finalized. Examine the updated reflection_ledger.json context.")
