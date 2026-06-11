# File: /home/keshanth/ARKA/ardhanarishvara/execution/ibkr_execution.py
#!/usr/bin/env python3
"""
IBKR Execution Layer
--------------------
Responsibilities:
    - Receive order instructions from Aruhan
    - Submit orders to IBKR via ib_insync
    - Handle confirmations, errors, and retries
    - Publish execution events back into IPC
    - Update ledger with executed order count and profit

This module is async-safe and fully decoupled from the rest of the system.
"""

import asyncio
from typing import Dict, Any

from ib_insync import IB, MarketOrder, Stock, util

from execution.ipc_broker import GlobalIPC
from execution.ledger import Ledger


class IBKRExecution:
    """
    Handles all communication with Interactive Brokers.
    """

    CHANNEL_IN = "execution.orders"
    CHANNEL_OUT = "execution.events"

    def __init__(self):
        self.ipc = GlobalIPC.get()
        self.ledger = Ledger()
        self.ib = IB()

    # ---------------------------------------------------------
    # Main Loop
    # ---------------------------------------------------------
    async def run(self):
        """
        Connects to IBKR and listens for incoming orders.
        """
        await self._connect()

        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            await self._handle_order(msg)

    # ---------------------------------------------------------
    # IBKR Connection
    # ---------------------------------------------------------
    async def _connect(self):
        """
        Connects to IBKR Gateway on localhost:7497.
        """
        print("[IBKR] Connecting to IB Gateway...")

        # ib_insync is synchronous, so run in thread
        await asyncio.to_thread(self.ib.connect, "127.0.0.1", 7497, clientId=1)

        if self.ib.isConnected():
            print("[IBKR] Connected successfully.")
        else:
            print("[IBKR] Connection failed. Retrying in 5 seconds...")
            await asyncio.sleep(5)
            await self._connect()

    # ---------------------------------------------------------
    # Order Handling
    # ---------------------------------------------------------
    async def _handle_order(self, msg: Dict[str, Any]):
        """
        Processes an incoming order instruction.
        """
        symbol = msg.get("symbol")
        action = msg.get("action", "BUY")
        quantity = msg.get("quantity", 1)

        if not symbol:
            print("[IBKR] Invalid order: missing symbol.")
            return

        print(f"[IBKR] Executing order: {action} {quantity} {symbol}")

        contract = Stock(symbol, "SMART", "USD")
        order = MarketOrder(action, quantity)

        try:
            trade = await asyncio.to_thread(self.ib.placeOrder, contract, order)
            await asyncio.to_thread(self.ib.sleep, 1)

            fill = trade.fills[-1] if trade.fills else None

            if fill:
                price = fill.price
                profit = msg.get("profit", 0.0)

                # Update ledger
                self.ledger.update_balance("orders_executed", 1)
                self.ledger.update_balance("profit_total", profit)

                # Publish execution event
                event = {
                    "symbol": symbol,
                    "action": action,
                    "quantity": quantity,
                    "price": price,
                    "profit": profit,
                    "executed": True,
                }

                await self.ipc.publish(self.CHANNEL_OUT, event)

                print(f"[IBKR] Order executed: {event}")

        except Exception as e:
            print("[IBKR] Order failed:", e)
            await self.ipc.publish(self.CHANNEL_OUT, {
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "executed": False,
                "error": str(e),
            })

    # ---------------------------------------------------------
    # Graceful Disconnect
