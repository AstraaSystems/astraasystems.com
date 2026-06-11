import re

class RuptureRepairEngine:
    """
    RUPTURE & REPAIR ENGINE
    Detects emotional ruptures and generates repair signals.
    Rupture indicators:
    - withdrawal
    - frustration
    - emotional shutdown
    - relational distancing
    - conflict language

    Repair logic:
    - acknowledge rupture
    - validate emotion
    - stabilize mood
    - restore connection
    """

    def __init__(self):
        self.rupture_patterns = {
            "withdrawal": [
                r"\bwhatever\b", r"\bforget it\b", r"\bnevermind\b",
                r"\bI don't care\b", r"\bdo what you want\b"
            ],
            "frustration": [
                r"\bI'm done\b", r"\bthis is stupid\b", r"\bwhy bother\b",
                r"\bI can't deal with this\b"
            ],
            "shutdown": [
                r"\bI give up\b", r"\bI can't talk\b", r"\bI'm tired of this\b"
            ],
            "distance": [
                r"\bleave me alone\b", r"\bdon't talk to me\b"
            ]
        }

    def detect_rupture(self, text):
        text_lower = text.lower()

        for rupture_type, patterns in self.rupture_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return rupture_type

        return None

    def repair_strategy(self, rupture_type, emotion, intensity):
        if rupture_type is None:
            return {
                "rupture": None,
                "repair_needed": False,
                "strategy": None
            }

        # Basic repair strategies
        strategies = {
            "withdrawal": "Acknowledge distance and gently re-engage.",
            "frustration": "Validate frustration and reduce emotional load.",
            "shutdown": "Stabilize emotional safety and slow the pace.",
            "distance": "Respect boundaries while signaling availability."
        }

        return {
            "rupture": rupture_type,
            "repair_needed": True,
            "strategy": strategies.get(rupture_type, "General emotional repair.")
        }

    def process(self, text, emotion, intensity):
        rupture_type = self.detect_rupture(text)
        return self.repair_strategy(rupture_type, emotion, intensity)
