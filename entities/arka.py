# File: /home/keshanth/ARKA/ardhanarishvara/entities/arka.py
#!/usr/bin/env python3
"""
Arka — Strategy Architect
-------------------------
Responsibilities:
    - Receive breakout signals
    - Transform them into strategy intents
"""

import asyncio
from typing import Dict, Any
from execution.ipc_broker import GlobalIPC


class Arka:
    CHANNEL_IN = "arka.strategy"
    CHANNEL_OUT = "aruhan.execution"

    def __init__(self):
        self.ipc = GlobalIPC.get()

    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            intent = self._build_intent(msg)
            await self.ipc.publish(self.CHANNEL_OUT, intent)

    def _build_intent(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        msg["arka_intent"] = True
        msg["intent_type"] = "evaluate"
        return msg


async def main():
    await Arka().run()


if __name__ == "__main__":
    asyncio.run(main())
