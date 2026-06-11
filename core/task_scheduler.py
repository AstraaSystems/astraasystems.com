# === AUTONOMOUS TASK SCHEDULER (V17 AUTONOMY‑READY) ===

import time
import json
import os
import threading

from core.kill_switch import kill_guard
from core.intent_engine import evaluate
from core.shadow_mode import shadow_simulate
from core.human_preference_learning import load_preferences
from agents.business_engine import business_engine
from agents.finance_engine import finance_engine
from agents.operations_engine import operations_engine

TASK_PATH = "/home/keshanth/ARKA/ardhanarishvara/core/task_queue.json"
_lock = threading.Lock()

DEFAULT_TASK_QUEUE = {
    "tasks": [],
    "last_run": None,
    "history": []
}

AGENT_MAP = {
    "business": business_engine,
    "finance": finance_engine,
    "operations": operations_engine
}


def _ensure_task_file():
    if not os.path.exists(TASK_PATH):
        with open(TASK_PATH, "w") as f:
            json.dump(DEFAULT_TASK_QUEUE, f, indent=4)


def add_task(agent, mode="run"):
    """
    Adds a task to the queue.
    mode = run | simulate | evolve
    """
    _ensure_task_file()

    with _lock:
        with open(TASK_PATH, "r") as f:
            queue = json.load(f)

        queue["tasks"].append({
            "agent": agent,
            "mode": mode,
            "timestamp": time.time()
        })

        with open(TASK_PATH, "w") as f:
            json.dump(queue, f, indent=4)

    return {"status": "task_added", "agent": agent, "mode": mode}


def get_next_task():
    _ensure_task_file()
    with _lock:
        with open(TASK_PATH, "r") as f:
            queue = json.load(f)

        if not queue["tasks"]:
            return None

        # Simple FIFO for now (can be upgraded to priority)
        return queue["tasks"][0]


def pop_task():
    _ensure_task_file()
    with _lock:
        with open(TASK_PATH, "r") as f:
            queue = json.load(f)

        if not queue["tasks"]:
            return None

        task = queue["tasks"].pop(0)

        with open(TASK_PATH, "w") as f:
            json.dump(queue, f, indent=4)

        return task


def execute_task(task):
    """
    Executes a task safely.
    """
    ks, reason = kill_guard()
    if ks:
        return {"status": "blocked_by_kill_switch", "reason": reason}

    agent_name = task["agent"]
    mode = task["mode"]

    agent_fn = AGENT_MAP.get(agent_name)
    if not agent_fn:
        return {"status": "invalid_agent", "agent": agent_name}

    # Apply preferences
    prefs = load_preferences()["preference_profile"]
    if prefs.get("prefers_simulation_first") and mode == "run":
        mode = "simulate"

    # Execute based on mode
    if mode == "simulate":
        return shadow_simulate(agent_name, agent_fn)

    if mode == "run":
        return agent_fn()

    return {"status": "unknown_mode", "mode": mode}


def scheduler_tick():
    """
    Runs one cycle of the scheduler.
    """
    ks, reason = kill_guard()
    if ks:
        return {"status": "halted_by_kill_switch", "reason": reason}

    task = get_next_task()
    if not task:
        return {"status": "idle", "reason": "no_tasks"}

    popped = pop_task()
    result = execute_task(popped)

    # Log result
    _ensure_task_file()
    with _lock:
        with open(TASK_PATH, "r") as f:
            queue = json.load(f)

        queue["history"].append({
            "task": popped,
            "result": result,
            "timestamp": time.time()
        })

        queue["last_run"] = time.time()

        with open(TASK_PATH, "w") as f:
            json.dump(queue, f, indent=4)

    return {
        "status": "task_executed",
        "task": popped,
        "result": result
    }
