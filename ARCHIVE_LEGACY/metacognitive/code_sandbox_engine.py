# ============================================================
# CODE SANDBOX ENGINE — Y‑PRIME EDITION
# ============================================================

import time
import threading

class CodeSandboxEngine:

    def __init__(self):
        self.lock = threading.Lock()
        self.history = []
        self.limits = {"history": 50}

    # ============================================================
    # EXECUTE SAFE CODE
    # ============================================================
    def execute(self, code):
        with self.lock:
            result = {"output": f"EXECUTED:{len(code)}", "ts": time.time()}
            self.history.append(result)
            if len(self.history) > self.limits["history"]:
                self.history.pop(0)
            return result

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {"executions": len(self.history)}
