# === HUMAN PREFERENCE LEARNING MODULE (V17 AUTONOMY‑READY) ===

import json
import os
import time
import threading

from core.kill_switch import kill_guard
from core.shadow_mode import shadow_simulate
from core.intent_engine import evaluate

PREF_PATH = "/home/keshanth/ARKA/ardhanarishvara/core/preferences.json"
_lock = threading.Lock()

DEFAULT_PREFS = {
    "last_update": None,
    "preference_profile": {},
    "history": []
}


def _ensure_pref_file():
    if not os.path.exists(PREF_PATH):
        with open(PREF_PATH, "w") as f:
            json.dump(DEFAULT_PREFS, f, indent=4)


def load_preferences():
    _ensure_pref_file()
    with _lock:
        with open(PREF_PATH, "r") as f:
            return json.load(f)


def save_preferences(prefs):
    with _lock:
        with open(PREF_PATH, "w") as f:
            json.dump(prefs, f, indent=4)


def record_user_action(action_text):
    """
    Logs user commands to learn preference patterns.
    """
    ks, reason = kill_guard()
    if ks:
        return {"status": "blocked_by_kill_switch", "reason": reason}

    prefs = load_preferences()

    prefs["history"].append({
        "timestamp": time.time(),
        "action": action_text
    })

    save_preferences(prefs)

    return {"status": "logged", "action": action_text}


def extract_preferences():
    """
    Learns preference patterns from user history.
    Example: If user often says 'simulate first', ARKA learns that.
    """

    prefs = load_preferences()
    history = prefs["history"]

    profile = {}

    # Simple pattern extraction
    for entry in history:
        text = entry["action"].lower()

        if "simulate" in text:
            profile["prefers_simulation_first"] = True

        if "evolve" in text:
            profile["prefers_evolution"] = True

        if "run finance" in text:
            profile["finance_priority"] = "high"

        if "run operations" in text:
            profile["operations_priority"] = "high"

    prefs["preference_profile"] = profile
    prefs["last_update"] = time.time()

    save_preferences(prefs)

    return {"status": "preferences_updated", "profile": profile}


def apply_preferences(agent_name, agent_fn, state):
    """
    Applies learned preferences to agent behavior.
    Runs in Shadow Mode first to ensure safety.
    """

    ks, reason = kill_guard()
    if ks:
        return {"status": "blocked_by_kill_switch", "reason": reason}

    prefs = load_preferences()["preference_profile"]

    # Example: If user prefers simulation-first
    if prefs.get("prefers_simulation_first"):
        sim = shadow_simulate(agent_name, agent_fn)
        if not sim["approved"]:
            return {
                "status": "blocked_by_intent",
                "violations": sim["violations"]
            }

    # Evaluate preference-aligned behavior
    intent = evaluate(agent_name, state)

    if not intent["approved"]:
        return {
            "status": "blocked_by_intent",
            "violations": intent["violations"]
        }

    return {
        "status": "preferences_applied",
        "intent_score": intent["score"],
        "preferences": prefs
    }
