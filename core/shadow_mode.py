# === SHADOW MODE (V17 AUTONOMY‑READY) ===

import json
import time
import copy
import threading
from core.blackboard import read_state
from core.intent_engine import evaluate
from core.kill_switch import kill_guard

SHADOW_LOG_PATH = "/home/keshanth/ARKA/ardhanarishvara/core/shadow_log.json"
_lock = threading.Lock()

DEFAULT_SHADOW_LOG = {
    "enabled": False,
    "last_run": None,
    "runs": []
}

def _ensure_shadow_log():
    if not os.path.exists(SHADOW_LOG_PATH):
        with open(SHADOW_LOG_PATH, "w") as f:
            json.dump(DEFAULT_SHADOW_LOG, f, indent=4)

def enable_shadow_mode():
    _ensure_shadow_log()
    with _lock:
        with open(SHADOW_LOG_PATH, "r") as f:
            log = json.load(f)

        log["enabled"] = True
        log["last_run"] = time.time()

        with open(SHADOW_LOG_PATH, "w") as f:
            json.dump(log, f, indent=4)

    return {"status": "shadow_mode_enabled"}

def disable_shadow_mode():
    _ensure_shadow_log()
    with _lock:
        with open(SHADOW_LOG_PATH, "r") as f:
            log = json.load(f)

        log["enabled"] = False

        with open(SHADOW_LOG_PATH, "w") as f:
            json.dump(log, f, indent=4)

    return {"status": "shadow_mode_disabled"}

def shadow_simulate(agent_name, agent_fn):
    """
    Runs an agent in simulation mode.
    Does NOT write to the blackboard.
    Does NOT affect the real system.
    """

    ks, reason = kill_guard()
    if ks:
        return {
            "status": "halted_by_kill_switch",
            "reason": reason
        }

    _ensure_shadow_log()

    # 1. Read real world state
    real_state = read_state()

    # 2. Create a deep copy for simulation
    simulated_state = copy.deepcopy(real_state)

    # 3. Run the agent logic on the simulated state
    result = agent_fn(simulated_state)

    # 4. Evaluate the simulated output with Intent Engine
    intent = evaluate(agent_name, result)

    # 5. Log the simulation
    with _lock:
        with open(SHADOW_LOG_PATH, "r") as f:
            log = json.load(f)

        log["runs"].append({
            "agent": agent_name,
            "timestamp": time.time(),
            "input_state": simulated_state,
            "output": result,
            "intent_score": intent["score"],
            "approved": intent["approved"],
            "violations": intent["violations"]
        })

        with open(SHADOW_LOG_PATH, "w") as f:
            json.dump(log, f, indent=4)

    return {
        "status": "shadow_simulation_complete",
        "agent": agent_name,
        "intent_score": intent["score"],
        "approved": intent["approved"],
        "violations": intent["violations"],
        "simulated_output": result
    }
