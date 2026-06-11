"""
Centralized Autonomy Audit Engine
Shared by ARKA, ASTRA, and ARUHAN
Located in: ardhanarishvara/autonomy/
"""

class AutonomyAudit:
    def __init__(self):
        self.history = []

    def record(self, event: str, details: dict = None):
        entry = {
            "event": event,
            "details": details or {}
        }
        self.history.append(entry)
        return entry

    def get_history(self):
        return self.history

    def summarize(self):
        return {
            "total_events": len(self.history),
            "events": self.history
        }
