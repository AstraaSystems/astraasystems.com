# File: /home/keshanth/ARKA/ardhanarishvara/infrastructure/environment.py
#!/usr/bin/env python3
"""
Environment Loader
------------------
Ensures required directories exist and loads environment variables.
"""

import os
from infrastructure.config import CONFIG


def initialize_environment():
    paths = CONFIG["paths"]

    for key, path in paths.items():
        if key == "ledger" or key == "kill_switch":
            continue
        os.makedirs(path, exist_ok=True)

    print("[ENV] Environment initialized.")
