# === NATURAL LANGUAGE COMMAND LAYER (V17 AUTONOMY‑READY) ===

import re
from core.kill_switch import activate_kill_switch, deactivate_kill_switch, kill_guard
from core.shadow_mode import shadow_simulate
from core.agent_evolution import evolve_agent
from core.blackboard import read_state
from agents.business_engine import business_engine
from agents.finance_engine import finance_engine
from agents.operations_engine import operations_engine


# --- COMMAND MAP -------------------------------------------------------------

COMMANDS = {
    "run business": lambda: business_engine(),
    "run finance": lambda: finance_engine(),
    "run operations": lambda: operations_engine(),

    "simulate business": lambda: shadow_simulate("business", business_engine),
    "simulate finance": lambda: shadow_simulate("finance", finance_engine),
    "simulate operations": lambda: shadow_simulate("operations", operations_engine),

    "evolve business": lambda: evolve_agent("business", business_engine),
    "evolve finance": lambda: evolve_agent("finance", finance_engine),
    "evolve operations": lambda: evolve_agent("operations", operations_engine),

    "kill": lambda: activate_kill_switch("manual override", "Keshanth"),
    "restore": lambda: deactivate_kill_switch("manual reset"),

    "status": lambda: read_state()
}


# --- NATURAL LANGUAGE PARSER -------------------------------------------------

def normalize(text):
    return text.lower().strip()


def match_command(text):
    """
    Matches natural language to a known command.
    """
    text = normalize(text)

    for key in COMMANDS.keys():
        if key in text:
            return key

    # Pattern-based fallback
    if "kill switch" in text or "emergency stop" in text:
        return "kill"

    if "restore" in text or "resume" in text:
        return "restore"

    if "status" in text or "state" in text:
        return "status"

    return None


# --- MAIN INTERFACE ----------------------------------------------------------

def arka_command(text):
    """
    Main entry point for natural language commands.
    """

    # Kill Switch check
    ks, reason = kill_guard()
    if ks and "restore" not in text.lower():
        return {
            "status": "blocked_by_kill_switch",
            "reason": reason
        }

    cmd = match_command(text)

    if not cmd:
        return {
            "status": "unknown_command",
            "message": f"I don't recognize the command: {text}"
        }

    try:
        result = COMMANDS[cmd]()
        return {
            "status": "success",
            "command": cmd,
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "command": cmd,
            "error": str(e)
        }
