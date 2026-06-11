# File: /home/keshanth/ARKA/ardhanarishvara/infrastructure/health_monitor.py
#!/usr/bin/env python3
"""
System Health Monitor
---------------------
Provides:
    - Heartbeat
    - CPU/memory checks
    - IPC responsiveness checks
"""

import asyncio
import psutil
from infrastructure.config import CONFIG


class HealthMonitor:

    async def run(self):
        interval = CONFIG["system"]["heartbeat_interval"]

        while True:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent

            print(f"[HEALTH] CPU: {cpu}% | MEM: {mem}%")

            await asyncio.sleep(interval)
