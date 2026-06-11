# File: /home/keshanth/ARKA/ardhanarishvara/execution/unified_engine.py
#!/usr/bin/env python3
"""
Unified Engine — Single‑Process Simulation Mode
-----------------------------------------------
This file contains a monolithic version of the entire Ardhanarishvara engine.
It is used for:
    - Debugging
    - Simulation
    - Offline testing
    - Verifying IPC flow
    - Running the system without launching multiple processes

This file includes:
    - IPC Broker
    - Math Engine
    - Treasury Agent
    - Ledger
    - IBKR Execution (Safe Mode Stub)
    - Lux / Astraa / Arka / Aruhan / Disturition
    - Autonomous Orchestrator

Production mode uses separate modules.
This file is for development and validation only.
"""

import asyncio
import json
import os
import threading
from datetime import datetime
from typing import Dict, Any, List


# ============================================================
# IPC BROKER (Embedded)
# ============================================================

class IPCBroker:
    def __init__(self):
        self.channels: Dict[str, asyncio.Queue] = {}
        self.log_dir = "/home/keshanth/ARKA/ardhanarishvara/ipc_logs"
        os.makedirs(self.log_dir, exist_ok=True)

    def _ensure(self, channel: str) -> asyncio.Queue:
        if channel not in self.channels:
            self.channels[channel] = asyncio.Queue()
        return self.channels[channel]

    async def publish(self, channel: str, message: Dict[str, Any]):
        q = self._ensure(channel)
        await q.put(message)
        self._log(channel, message)

    async def subscribe(self, channel: str):
        q = self._ensure(channel)
        while True:
            msg = await q.get()
            yield msg

    def _log(self, channel: str, message: Dict[str, Any]):
        date = datetime.now().strftime("%Y-%m-%d")
        path = f"{self.log_dir}/{date}.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "channel": channel,
            "message": message,
        }
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")


class GlobalIPC:
    _instance: IPCBroker = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = IPCBroker()
        return cls._instance


# ============================================================
# LEDGER (Embedded)
# ============================================================

class Ledger:
    LEDGER_PATH = "/home/keshanth/ARKA/ardhanarishvara/ledger.json"

    def __init__(self):
        self.lock = threading.Lock()
        self._ensure()

    def _ensure(self):
        if not os.path.exists(self.LEDGER_PATH):
            initial = {
                "income_total": 0.0,
                "harvested_total": 0.0,
                "retained_total": 0.0,
                "TFSA": 0.0,
                "RRSP": 0.0,
                "RESP": 0.0,
                "orders_executed": 0,
                "profit_total": 0.0,
            }
            self._write(initial)

    def _read(self):
        with open(self.LEDGER_PATH, "r") as f:
            return json.load(f)

    def _write(self, state):
        with open(self.LEDGER_PATH, "w") as f:
            json.dump(state, f, indent=4)

    def update(self, key: str, amount: float):
        with self.lock:
            state = self._read()
            state[key] = round(state.get(key, 0.0) + amount, 2)
            self._write(state)

    def get(self, key: str):
        with self.lock:
            return self._read().get(key)


# ============================================================
# MATH ENGINE (Embedded)
# ============================================================

class MathEngine:
    CHANNEL_IN = "market.data"
    CHANNEL_OUT = "arka.strategy"
    WINDOW = 20

    def __init__(self):
        self.ipc = GlobalIPC.get()
        self.prices: List[float] = []

    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            signal = self._tick(msg)
            if signal:
                await self.ipc.publish(self.CHANNEL_OUT, signal)

    def _tick(self, msg):
        price = msg.get("price")
        symbol = msg.get("symbol", "UNKNOWN")
        if price is None:
            return None

        self.prices.append(price)
        if len(self.prices) > self.WINDOW:
            self.prices.pop(0)

        if len(self.prices) < self.WINDOW:
            return None

        high = max(self.prices)
        low = min(self.prices)
        volatility = high - low

        if volatility < 0.10:
            return None

        if price >= high:
            return {"symbol": symbol, "price": price, "action": "BUY"}

        if price <= low:
            return {"symbol": symbol, "price": price, "action": "SELL"}

        return None


# ============================================================
# TREASURY AGENT (Embedded)
# ============================================================

class TreasuryAgent:
    CHANNEL_IN = "astraa.output"
    CHANNEL_OUT = "treasury.updates"

    def __init__(self):
        self.ipc = GlobalIPC.get()
        self.ledger = Ledger()

    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            processed = self._process(msg)
            await self.ipc.publish(self.CHANNEL_OUT, processed)

    def _process(self, msg):
        amount = msg.get("amount", 0.0)
        harvested = round(amount * 0.20, 2)
        retained = round(amount - harvested, 2)
        split = round(harvested / 3, 2)

        allocation = {"TFSA": split, "RRSP": split, "RESP": split}

        self.ledger.update("income_total", amount)
        self.ledger.update("harvested_total", harvested)
        self.ledger.update("retained_total", retained)
        for k, v in allocation.items():
            self.ledger.update(k, v)

        msg.update({
            "harvested": harvested,
            "retained": retained,
            "allocation": allocation,
            "treasury_processed": True,
        })
        return msg


# ============================================================
# IBKR EXECUTION (SAFE MODE)
# ============================================================

class IBKRExecution:
    CHANNEL_IN = "execution.orders"
    CHANNEL_OUT = "execution.events"

    def __init__(self):
        self.ipc = GlobalIPC.get()
        self.ledger = Ledger()

    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            await self._simulate(msg)

    async def _simulate(self, msg):
        """
        Safe mode: does NOT connect to IBKR.
        Used for simulation/testing.
        """
        symbol = msg.get("symbol")
        action = msg.get("action")
        qty = msg.get("quantity", 1)

        event = {
            "symbol": symbol,
            "action": action,
            "quantity": qty,
            "executed": True,
            "price": msg.get("price", 0.0),
            "profit": msg.get("profit", 0.0),
        }

        self.ledger.update("orders_executed", 1)
        self.ledger.update("profit_total", event["profit"])

        await self.ipc.publish(self.CHANNEL_OUT, event)


# ============================================================
# ENTITIES (Embedded)
# ============================================================

class Lux:
    CHANNEL_IN = "lux.intake"
    CHANNEL_OUT = "lux.output"

    def __init__(self):
        self.ipc = GlobalIPC.get()

    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            msg["lux_clarity"] = True
            await self.ipc.publish(self.CHANNEL_OUT, msg)


class Astraa:
    CHANNEL_IN = "astraa.income"
    CHANNEL_OUT = "astraa.output"

    def __init__(self):
        self.ipc = GlobalIPC.get()

    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            msg["astraa_routed"] = True
            await self.ipc.publish(self.CHANNEL_OUT, msg)


class Arka:
    CHANNEL_IN = "arka.strategy"
    CHANNEL_OUT = "aruhan.execution"

    def __init__(self):
        self.ipc = GlobalIPC.get()

    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            msg["arka_intent"] = True
            await self.ipc.publish(self.CHANNEL_OUT, msg)


class Aruhan:
    CHANNEL_IN = "aruhan.execution"
    CHANNEL_OUT = "execution.orders"

    def __init__(self):
        self.ipc = GlobalIPC.get()

    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            msg["order_prepared"] = True
            msg["quantity"] = msg.get("quantity", 1)
            await self.ipc.publish(self.CHANNEL_OUT, msg)


class Disturition:
    CHANNEL_IN = "disturition.alerts"
    CHANNEL_OUT = "system.kill"

    def __init__(self):
        self.ipc = GlobalIPC.get()

    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            if msg.get("severity") == "critical":
                await self.ipc.publish(self.CHANNEL_OUT, {"kill": True})


# ============================================================
# AUTONOMOUS ORCHESTRATOR (Embedded)
# ============================================================

class UnifiedAutonomousSystem:
    def __init__(self):
        self.ipc = GlobalIPC.get()
        self.tasks = []
        self.running = True

    async def start(self):
        modules = [
            MathEngine().run(),
            TreasuryAgent().run(),
            IBKRExecution().run(),
            Lux().run(),
            Astraa().run(),
            Arka().run(),
            Aruhan().run(),
            Disturition().run(),
            self._heartbeat(),
        ]

        for m in modules:
            self.tasks.append(asyncio.create_task(m))

        await asyncio.gather(*self.tasks)

    async def _heartbeat(self):
        while self.running:
            print("[UNIFIED] Heartbeat — system alive.")
            await asyncio.sleep(5)


# ============================================================
# ENTRY POINT
# ============================================================

async def main():
    system = UnifiedAutonomousSystem()
    await system.start()


if __name__ == "__main__":
    asyncio.run(main())
