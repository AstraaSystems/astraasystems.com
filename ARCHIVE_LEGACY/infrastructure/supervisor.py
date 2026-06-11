# File: /home/keshanth/ARKA/ardhanarishvara/infrastructure/supervisor.py
#!/usr/bin/env python3
"""
Supervisor Utilities
--------------------
Provides restart helpers and crash handling utilities.
"""

import asyncio
import traceback
from infrastructure.config import CONFIG


async def supervise(coro):
    """
    Wraps a coroutine in a restart loop.
    """
    delay = CONFIG["system"]["supervisor_restart_delay"]

    while True:
        try:
            await coro
        except Exception as e:
            print("[SUPERVISOR] Module crashed:", e)
            traceback.print_exc()
            print(f"[SUPERVISOR] Restarting in {delay} seconds...")
            await asyncio.sleep(delay)
