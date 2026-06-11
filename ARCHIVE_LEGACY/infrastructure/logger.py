# File: /home/keshanth/ARKA/ardhanarishvara/infrastructure/logger.py
#!/usr/bin/env python3
"""
Unified Logging Interface
-------------------------
Writes logs to /logs/system/YYYY-MM-DD.log
"""

import os
from datetime import datetime
from infrastructure.config import CONFIG


class Logger:

    def __init__(self):
        self.log_dir = CONFIG["paths"]["system_logs"]
        os.makedirs(self.log_dir, exist_ok=True)

    def log(self, message: str):
        date = datetime.now().strftime("%Y-%m-%d")
        path = f"{self.log_dir}/{date}.log"

        entry = f"[{datetime.now().isoformat()}] {message}\n"

        with open(path, "a") as f:
            f.write(entry)

        print(entry.strip())
