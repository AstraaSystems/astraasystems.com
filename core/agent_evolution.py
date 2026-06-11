# === AGENT EVOLUTION ENGINE (V17 AUTONOMY‑READY) ===

import json
import time
import copy
import os
import threading

from core.shadow_mode import shadow_simulate
from core.intent_engine import evaluate
from core.kill_switch import kill_guard

EVOLUTION_LOG_PATH = "/home/keshanth/ARKA/ardhanarishvara/core/evolution_log.json"
_lock = threading.Lock()

DEFAULT_EVOLUTION_LOG = {
    "enabled": True,
    "last_evolution": None,
    "history": []
}

def _ensure_log():
    if not os.path.exists(EVOLUTION_LOG_PATH):
        with open(EVOLUTION_LOG_PATH, "w") as f:
            json.dump(DEFAULT_EVOLUTION_LOG, f, indent=4)

def enable_evolution():
    _ensure_log()
    with _lock:
        with open(EVOLUTION_LOG_PATH, "r") as f:
            log = json.load(f)

        log["enabled"] = True

        with open(EVOLUTION_LOG_PATH, "w") as f:
            json.dump(log, f, indent=4)

    return {"status": "evolution_enabled"}

def disable_evolution():
    _ensure_log()
    with _lock:
        with open(EVOLUTION_LOG_PATH, "r") as f:
            log = json.load(f)

        log["enabled"] = False

        with open(EVOLUTION_LOG_PATH, "w") as f:
            json.dump(log, f, indent=4)

    return {"status": "evolution_disabled"}


def mutate_agent(agent_fn):
    """
    Creates a mutated version of an agent.
    This is SAFE mutation: small, controlled, reversible.
    """

    def mutated(simulated_state):
        output = agent_fn(simulated_state)

        # Example mutation: adjust numeric fields slightly
        for key, value in output.items():
            if isinstance(value, (int, float)):
                output[key] = value * 1.02  # +2% mutation

        output["mutation_tag"] = "v17_mutation"
        return output

    return mutated


def evolve_agent(agent_name, agent_fn):
    """
    Full evolution pipeline:
    - Clone agent
    - Mutate agent
    - Run in Shadow Mode
    - Evaluate with Intent Engine
    - Compare performance
    - Log results
    """

    ks, reason = kill_guard()
    if ks:
        return {
            "status": "halted_by_kill_switch",
            "reason": reason
        }

    _ensure_log()

    # 1. Create mutated agent
    mutated_agent = mutate_agent(agent_fn)

    # 2. Run simulation
    sim_result = shadow_simulate(agent_name, mutated_agent)

    # 3. Evaluate improvement
    improvement = {
        "approved": sim_result["approved"],
        "intent_score": sim_result["intent_score"],
        "violations": sim_result["violations"],
        "simulated_output": sim_result["simulated_output"]
    }

    # 4. Log evolution attempt
    with _lock:
        with open(EVOLUTION_LOG_PATH, "r") as f:
            log = json.load(f)

        log["last_evolution"] = time.time()
        log["history"].append({
            "agent": agent_name,
            "timestamp": time.time(),
            "result": improvement
        })

        with open(EVOLUTION_LOG_PATH, "w") as f:
            json.dump(log, f, indent=4)

    return {
        "status": "evolution_complete",
        "agent": agent_name,
        "improvement": improvement
    }
