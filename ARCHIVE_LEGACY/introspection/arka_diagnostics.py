"""
Centralized Diagnostics Engine
Shared by ARKA, ASTRA, and ARUHAN
Located in: ardhanarishvara/introspection/
"""

import time
import traceback


class DiagnosticsEngine:
    def __init__(self):
        self.logs = []

    def log(self, message: str, level: str = "INFO"):
        entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        return entry

    def error(self, message: str, exception: Exception = None):
        entry = {
            "timestamp": time.time(),
            "level": "ERROR",
            "message": message,
            "trace": traceback.format_exc() if exception else None
        }
        self.logs.append(entry)
        return entry

    def get_logs(self):
        return self.logs

    def summarize(self):
        return {
            "total_logs": len(self.logs),
            "errors": [log for log in self.logs if log["level"] == "ERROR"],
            "info": [log for log in self.logs if log["level"] == "INFO"]
        }
