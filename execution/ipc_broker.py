# File: /home/keshanth/ARKA/ardhanarishvara/execution/ipc_broker.py
#!/usr/bin/env python3
"""
Hybrid Multi‑Queue IPC Broker (Global Singleton)
Local-only, async-safe, zero external dependencies.

This broker provides:
    - Per-channel asyncio queues
    - Publish/subscribe messaging
    - Global singleton access
    - Optional persistent JSONL logging
    - Deterministic message ordering

All agents and execution modules communicate ONLY through this broker.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, AsyncGenerator


class IPCBroker:
    """
    Core broker class.
    Manages channels, queues, logging, and async message routing.
    """

    def __init__(self):
        self.channels: Dict[str, asyncio.Queue] = {}
        self.log_dir = "/home/keshanth/ARKA/ardhanarishvara/ipc_logs"
        os.makedirs(self.log_dir, exist_ok=True)

    # ---------------------------------------------------------
    # Channel Management
    # ---------------------------------------------------------
    def _ensure_channel(self, channel: str) -> asyncio.Queue:
        if channel not in self.channels:
            self.channels[channel] = asyncio.Queue()
        return self.channels[channel]

    # ---------------------------------------------------------
    # Publish
    # ---------------------------------------------------------
    async def publish(self, channel: str, message: Dict[str, Any]) -> None:
        """
        Publish a message to a channel.
        Creates the channel if it doesn't exist.
        Logs the message to JSONL.
        """
        queue = self._ensure_channel(channel)
        await queue.put(message)
        self._log_message(channel, message)

    # ---------------------------------------------------------
    # Subscribe
    # ---------------------------------------------------------
    async def subscribe(self, channel: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Async generator that yields messages from a channel.
        Creates the channel if it doesn't exist.
        """
        queue = self._ensure_channel(channel)
        while True:
            msg = await queue.get()
            yield msg

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------
    def _log_message(self, channel: str, message: Dict[str, Any]) -> None:
        """
        Writes each message to a daily JSONL log file.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"{date_str}.jsonl")

        entry = {
            "timestamp": datetime.now().isoformat(),
            "channel": channel,
            "message": message,
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")


# ============================================================
# Global Singleton Access
# ============================================================

class GlobalIPC:
    """
    Singleton wrapper so every module uses the same broker instance.
    """
    _instance: IPCBroker = None

    @classmethod
    def get(cls) -> IPCBroker:
        if cls._instance is None:
            cls._instance = IPCBroker()
        return cls._instance


# ============================================================
# Standalone Test Harness
# ============================================================

async def _test():
    ipc = GlobalIPC.get()

    async def producer():
        for i in range(3):
            await ipc.publish("test.channel", {"count": i})
            await asyncio.sleep(0.1)

    async def consumer():
        async for msg in ipc.subscribe("test.channel"):
            print("Received:", msg)

    await asyncio.gather(producer(), consumer())


if __name__ == "__main__":
    asyncio.run(_test())
