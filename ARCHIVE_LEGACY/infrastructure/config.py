# File: /home/keshanth/ARKA/ardhanarishvara/infrastructure/config.py
#!/usr/bin/env python3
"""
Central Configuration Registry
------------------------------
Stores all system paths, constants, and environment flags.
"""

BASE = "/home/keshanth/ARKA/ardhanarishvara"

CONFIG = {
    "paths": {
        "base": BASE,
        "ipc_logs": f"{BASE}/ipc_logs",
        "ledger": f"{BASE}/ledger.json",
        "kill_switch": f"{BASE}/kill.switch",
        "system_logs": f"{BASE}/logs/system",
    },
    "system": {
        "heartbeat_interval": 5,
        "supervisor_restart_delay": 2,
    }
}
