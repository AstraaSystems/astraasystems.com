# File: /home/keshanth/ARKA/ardhanarishvara/execution/math_engine.py
#!/usr/bin/env python3
"""
Math Engine — Breakout & Signal Generator
-----------------------------------------
Responsibilities:
    - Receive market data events
    - Compute breakout conditions
    - Apply volatility filters
    - Emit BUY/SELL/HOLD signals
    - Publish strategy triggers to Arka

This module is intentionally simple, deterministic, and stable.
"""

import asyncio
from typing import Dict, Any, List

from execution.ipc_broker import GlobalIPC


class MathEngine:
    """
    Breakout logic:
        - Rolling window high/low
        - Simple volatility filter
        - Signal generation
    """

    CHANNEL_IN = "market.data"
    CHANNEL_OUT = "arka.strategy"

    WINDOW = 20  # rolling window size

    def __init__(self):
        self.ipc = GlobalIPC.get()
        self.prices: List[float] = []

    # ---------------------------------------------------------
    # Main Loop
    # ---------------------------------------------------------
    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            signal = self._process_tick(msg)
            if signal:
                await self.ipc.publish(self.CHANNEL_OUT, signal)

    # ---------------------------------------------------------
    # Tick Processing
    # ---------------------------------------------------------
    def _process_tick(self, msg: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Processes each incoming price tick.
        """
        price = msg.get("price")
        symbol = msg.get("symbol", "UNKNOWN")

        if price is None:
            return None

        # Update rolling window
        self.prices.append(price)
        if len(self.prices) > self.WINDOW:
            self.prices.pop(0)

        # Not enough data yet
        if len(self.prices) < self.WINDOW:
            return None

        high = max(self.prices)
        low = min(self.prices)

        # Volatility filter
        volatility = high - low
        if volatility < 0.10:  # too flat
            return None

        # Breakout logic
        if price >= high:
            return self._build_signal(symbol, price, "BUY")

        if price <= low:
            return self._build_signal(symbol, price, "SELL")

        return None

    # ---------------------------------------------------------
    # Signal Builder
    # ---------------------------------------------------------
    def _build_signal(self, symbol: str, price: float, action: str) -> Dict[str, Any]:
        """
        Builds a structured signal message.
        """
        return {
            "symbol": symbol,
            "price": price,
            "action": action,
            "math_engine_signal": True,
        }


# ============================================================
# Entry Point
# ============================================================

async def main():
    engine = MathEngine()
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main())
