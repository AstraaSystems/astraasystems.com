"""
Valid transitions for ARKA Extended State Machine
"""

VALID_TRANSITIONS = {
    "idle": ["running", "shutdown"],
    "running": ["paused", "waiting", "blocked", "error", "shutdown"],
    "paused": ["running", "shutdown"],
    "waiting": ["running", "blocked", "error", "shutdown"],
    "blocked": ["recovering", "shutdown"],
    "recovering": ["running", "error", "shutdown"],
    "error": ["recovering", "shutdown"],
    "shutdown": []
}
