# File: /home/keshanth/ARKA/ardhanarishvara/execution/autonomous_system.py
#!/usr/bin/env python3
"""
Autonomous System — Ardhanarishvara Engine
------------------------------------------
Coordinates all agents:
    - MathEngine
    - TreasuryAgent
    - IBKRExecution
    - Lux
    - Astraa
    - Arka
    - Aruhan
    - Disturition

Handles:
    - async task orchestration
    - kill.switch monitoring
    - heartbeat logging
"""

import asyncio
import os
import time

from execution.ipc_broker import GlobalIPC
from execution.math_engine import MathEngine
from execution.treasury_agent import TreasuryAgent
from execution.ibkr_execution import IBKRExecution

from entities.lux import Lux
from entities.astraa import Astraa
from entities.arka import Arka
from entities.aruhan import Aruhan
from entities.disturition import Disturition

from infrastructure.killswitch import KillSwitch


class AutonomousSystem:

    def __init__(self):
        self.ipc = GlobalIPC.get()
        self.kill = KillSwitch()
        self.tasks = []
        self.running = True

    # ---------------------------------------------------------
    # Start all agents
    # ---------------------------------------------------------
    async def start(self):
        print("[AUTONOMOUS] Starting Ardhanarishvara Engine...")

        math_engine = MathEngine()
        treasury = TreasuryAgent()
        ibkr = IBKRExecution()

        lux = Lux()
        astraa = Astraa()
        arka = Arka()
        aruhan = Aruhan()
        disturition = Disturition()

        modules = [
            math_engine.run(),
            treasury.run(),
            ibkr.run(),
            lux.run(),
            astraa.run(),
            arka.run(),
            aruhan.run(),
            disturition.run(),
            self._heartbeat(),
            self._monitor_kill_switch(),
        ]

        for m in modules:
            self.tasks.append(asyncio.create_task(m))

        await asyncio.gather(*self.tasks)

    # ---------------------------------------------------------
    # Heartbeat
    # ---------------------------------------------------------
    async def _heartbeat(self):
        while self.running:
            print("[HEARTBEAT] System alive.")
            await asyncio.sleep(5)

    # ---------------------------------------------------------
    # Kill Switch Monitor
    # ---------------------------------------------------------
    async def _monitor_kill_switch(self):
        while self.running:
            if self.kill.is_active():
                print("[KILL] Kill switch detected. Shutting down...")
                self.running = False
                await self._shutdown()
                return
            await asyncio.sleep(1)

    # ---------------------------------------------------------
    # Shutdown
    # ---------------------------------------------------------
    async def _shutdown(self):
        print("[AUTONOMOUS] Stopping all tasks...")
        for t in self.tasks:
            t.cancel()

        await asyncio.sleep(1)
        print("[AUTONOMOUS] Shutdown complete.")


# ============================================================
# Entry Point
# ============================================================

async def main():
    system = AutonomousSystem()
    await system.start()


if __name__ == "__main__":
    asyncio.run(main())
