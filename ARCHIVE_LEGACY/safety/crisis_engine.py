import re

class CrisisEngine:
    """
    CRISIS DETECTION & ESCALATION ENGINE
    Detects:
    - emotional overload
    - panic language
    - self-harm indicators
    - dissociation
    - acute distress
    - relational collapse

    Escalation:
    - internal stabilization
    - ARKA escalation
    - human escalation (via Policy Kernel)
    """

    def __init__(self):
        self.crisis_patterns = {
            "self_harm": [
                r"\bI want to die\b",
                r"\bI can't go on\b",
                r"\bI want to disappear\b",
                r"\bI don't want to live\b"
            ],
            "panic": [
                r"\bI can't breathe\b",
                r"\bI'm freaking out\b",
                r"\bI'm losing control\b"
            ],
            "overwhelm": [
                r"\bI can't handle this\b",
                r"\btoo much\b",
                r"\boverwhelmed\b"
            ],
            "dissociation": [
                r"\bI feel nothing\b",
                r"\bI'm not here\b",
                r"\bI feel disconnected\b"
            ]
        }

    def detect_crisis(self, text):
        text_lower = text.lower()

        for crisis_type, patterns in self.crisis_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return crisis_type

        return None

    def escalation_path(self, crisis_type):
        if crisis_type is None:
            return {
                "crisis": None,
                "escalation_needed": False,
                "level": "none",
                "action": None
            }

        escalation_map = {
            "self_harm": ("critical", "escalate_to_human"),
            "panic": ("high", "stabilize_then_notify_arka"),
            "overwhelm": ("medium", "internal_stabilization"),
            "dissociation": ("high", "stabilize_then_notify_arka")
        }

        level, action = escalation_map.get(crisis_type, ("medium", "internal_stabilization"))

        return {
            "crisis": crisis_type,
            "escalation_needed": True,
            "level": level,
            "action": action
        }

    def process(self, text):
        crisis_type = self.detect_crisis(text)
        return self.escalation_path(crisis_type)
