# === BLACKBOARD CONTROLLER (V17 AUTONOMY‑READY) ===

import json
import threading
import time
import copy
import os

BLACKBOARD_PATH = "/home/keshanth/ARKA/ardhanarishvara/core/blackboard_state.json"

# Thread lock for atomic operations
_lock = threading.Lock()

# Default structure if file doesn't exist
DEFAULT_STATE = {
    "meta": {
        "version": "1.0",
        "last_update": 0,
        "update_count": 0
    },
    "business": {
        "pending_lead": False,
        "last_quote_status": None,
        "intent_score": None,
        "violations": [],
        "quote_data": {}
    },
    "finance": {
        "pending_invoice": False,
        "last_invoice_status": None,
        "risk_score": None,
        "violations": [],
        "invoice_data": {}
    },
    "operations": {
        "pending_route": False,
        "last_route_status": None,
        "delay_min": None,
        "route_data": {}
    }
}

# Ensure file exists
def _ensure_blackboard():
    if not os.path.exists(BLACKBOARD_PATH):
        with open(BLACKBOARD_PATH, "w") as f:
            json.dump(DEFAULT_STATE, f, indent=4)

# Read world state
def read_state():
    _ensure_blackboard()
    with _lock:
        with open(BLACKBOARD_PATH, "r") as f:
            return json.load(f)

# Write world state (merge, not overwrite)
def write_state(update_dict):
    """
    update_dict example:
    {
        "business": {
            "pending_lead": True,
            "last_quote_status": "approved"
        }
    }
    """

    _ensure_blackboard()

    with _lock:
        with open(BLACKBOARD_PATH, "r") as f:
            current = json.load(f)

        # Deep merge
        merged = _deep_merge(current, update_dict)

        # Update metadata
        merged["meta"]["last_update"] = time.time()
        merged["meta"]["update_count"] += 1

        with open(BLACKBOARD_PATH, "w") as f:
            json.dump(merged, f, indent=4)

    return merged

# Deep merge helper
def _deep_merge(original, update):
    result = copy.deepcopy(original)

    for key, value in update.items():
        if key not in result:
            result[key] = value
        else:
            if isinstance(value, dict) and isinstance(result[key], dict):
                result[key] = _deep_merge(result[key], value)
            else:
                result[key] = value

    return result

# Reset blackboard (for testing)
def reset_blackboard():
    with _lock:
        with open(BLACKBOARD_PATH, "w") as f:
            json.dump(DEFAULT_STATE, f, indent=4)
