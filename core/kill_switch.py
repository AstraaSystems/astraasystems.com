# === KILL SWITCH (V17 AUTONOMY‑READY) ===

import json
import threading
import time
import os

KILL_PATH = "/home/keshanth/ARKA/ardhanarishvara/core/kill_state.json"

_lock = threading.Lock()

DEFAULT_KILL_STATE = {
    "kill_switch": False,
    "reason": None,
    "ts": 0,
    "activated_by": None,
    "audit_log": []
}

def _ensure_file():
    if not os.path.exists(KILL_PATH):
        with open(KILL_PATH, "w") as f:
            json.dump(DEFAULT_KILL_STATE, f, indent=4)

def read_kill_state():
    _ensure_file()
    with _lock:
        with open(KILL_PATH, "r") as f:
            return json.load(f)

def activate_kill_switch(reason="unspecified", activated_by="human"):
    """
    Activates the kill switch and logs the event.
    """
    _ensure_file()
    with _lock:
        with open(KILL_PATH, "r") as f:
            state = json.load(f)

        state["kill_switch"] = True
        state["reason"] = reason
        state["activated_by"] = activated_by
        state["ts"] = time.time()

        state["audit_log"].append({
            "event": "KILL_SWITCH_ACTIVATED",
            "reason": reason,
            "activated_by": activated_by,
            "ts": time.time()
        })

        with open(KILL_PATH, "w") as f:
            json.dump(state, f, indent=4)

    return state

def deactivate_kill_switch(activated_by="human"):
    """
    Resets the kill switch safely.
    """
    _ensure_file()
    with _lock:
        with open(KILL_PATH, "r") as f:
            state = json.load(f)

        state["kill_switch"] = False
        state["reason"] = None
        state["activated_by"] = activated_by
        state["ts"] = time.time()

        state["audit_log"].append({
            "event": "KILL_SWITCH_DEACTIVATED",
            "activated_by": activated_by,
            "ts": time.time()
        })

        with open(KILL_PATH, "w") as f:
            json.dump(state, f, indent=4)

    return state

def kill_guard():
    """
    Agents call this before performing any action.
    If kill switch is active, they must stop immediately.
    """
    state = read_kill_state()
    return state["kill_switch"], state["reason"]
