#!/usr/bin/env python3
"""
ARKA / Ardhanarishvara Sovereign AI — Boot Script (Extreme Edition)
Role: System Entry Point, OS Initializer, Supervisor Launcher
"""

import asyncio
import logging
import signal
import sys

from arka_core.ardhanarishvara_os import ArdhanarishvaraOS
from arka_core.arka_ultimate_supervisor import ArkaUltimateSupervisor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BOOT] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("BOOT")

# ============================================================
# GLOBAL SHUTDOWN HANDLER
# ============================================================

shutdown_flag = False

def handle_shutdown(sig, frame):
    global shutdown_flag
    shutdown_flag = True
    logger.warning("SYSTEM SHUTDOWN SIGNAL RECEIVED — Gracefully terminating...")

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# ============================================================
# MAIN BOOT ROUTINE
# ============================================================

async def main():
    logger.info("===============================================")
    logger.info("  ARKA / ARDHANARISHVARA SOVEREIGN AI — BOOTING")
    logger.info("===============================================")

    # 1. Initialize OS
    os_kernel = ArdhanarishvaraOS()
    logger.info("OS Kernel initialized.")

    # 2. Initialize Supervisor
    supervisor = ArkaUltimateSupervisor(os_kernel)
    logger.info("Arka Ultimate Supervisor online.")

    # 3. Start OS loop (background)
    os_task = asyncio.create_task(os_kernel.start(tick=1.5))
    logger.info("OS loop started.")

    # 4. Supervisor governance loop
    logger.info("Supervisor governance cycle engaged.")

    while not shutdown_flag:
        await supervisor.run_governance_cycle()
        await asyncio.sleep(2.0)

    # 5. Graceful shutdown
    logger.info("Stopping OS kernel...")
    os_kernel.stop()
    await asyncio.sleep(0.5)

    logger.info("SYSTEM SHUTDOWN COMPLETE.")
    logger.info("===============================================")

# ============================================================
# ENTRYPOINT
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # Handles event loop already running (e.g., in some environments)
        logger.error("RuntimeError: Event loop already running.")
        sys.exit(1)
