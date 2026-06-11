import datetime
from typing import Dict, Any
from domains.data_oracle.oracle import run_data_oracle_node
from domains.vsv_ai.core.vsv_router import route_vsv_execution

def resolve_5w_matrix(intent: dict) -> Dict[str, Any]:
    target = intent.get("target_domain")
    return {
        "WHO": f"Aruhan.Kernel.Engine.{target.upper() if target else 'SYSTEM'}",
        "WHAT": intent.get("action", "STATE_AUDIT"),
        "WHEN": f"{datetime.datetime.utcnow().isoformat()}Z",
        "WHERE": "IsolatedKernelSpace",
        "WHY": f"Sovereign request initiated with access clearance code: '{intent.get('origin')}'"
    }

def process_execution_lifecycle(authenticated_intent: dict) -> Dict[str, Any]:
    execution_matrix = resolve_5w_matrix(authenticated_intent)
    target_domain = authenticated_intent.get("target_domain")
    payload_data = authenticated_intent.get("data", {})
    
    if target_domain == "vsv_ai":
        oracle_payload = run_data_oracle_node(payload_data)
        metrics = oracle_payload["state_estimation"]
        vsv_input = {
            "velocity": metrics["velocity"],
            "volatility": payload_data.get("volatility", 0.0)
        }
        vsv_output = route_vsv_execution(authenticated_intent.get("action"), vsv_input)
        domain_output = {"analytical_truth": oracle_payload, "real_world_action": vsv_output}
    else:
        domain_output = {"status": "ROUTING_PASS", "message": "Standard execution thread."}
        
    return {
        "kernel_5w_ledger": execution_matrix,
        "returned_state": domain_output
    }
