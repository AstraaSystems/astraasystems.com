# File: /home/keshanth/ARKA/ardhanarishvara/infrastructure/killswitch.py
#!/usr/bin/env python3
"""
Kill Switch Handler
-------------------
Provides safe shutdown signaling via kill.switch file.
"""

import os
from infrastructure.config import CONFIG


class KillSwitch:

    def __init__(self):
        self.path = CONFIG["paths"]["kill_switch"]

    def activate(self):
        with open(self.path, "w") as f:
            f.write("KILL")
        print("[KILL] kill.switch activated.")

    def deactivate(self):
        if os.path.exists(self.path):
            os.remove(self.path)
            print("[KILL] kill.switch removed.")

    def is_active(self) -> bool:
        return os.path.exists(self.path)
