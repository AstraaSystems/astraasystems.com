# File: /home/keshanth/ARKA/ardhanarishvara/execution/treasury_agent.py
#!/usr/bin/env python3
"""
Treasury Agent — Income Allocation & Harvesting
------------------------------------------------
Responsibilities:
    - Receive income events from Astraa
    - Apply 20% harvesting rule
    - Allocate harvested funds to TFSA/RRSP/RESP buckets
    - Update ledger state
    - Publish treasury updates to IPC channels

This module ensures all income is routed correctly and consistently.
"""

import asyncio
from typing import Dict, Any

from execution.ipc_broker import GlobalIPC
from execution.ledger import Ledger


class TreasuryAgent:
    """
    Treasury logic:
        - 20% harvesting
        - TFSA/RRSP/RESP allocation
        - Ledger updates
    """

    CHANNEL_IN = "astraa.output"
    CHANNEL_OUT = "treasury.updates"

    def __init__(self):
        self.ipc = GlobalIPC.get()
        self.ledger = Ledger()

    # ---------------------------------------------------------
    # Main Loop
    # ---------------------------------------------------------
    async def run(self):
        async for msg in self.ipc.subscribe(self.CHANNEL_IN):
            processed = self._process_income(msg)
            await self.ipc.publish(self.CHANNEL_OUT, processed)

    # ---------------------------------------------------------
    # Income Processing
    # ---------------------------------------------------------
    def _process_income(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies harvesting and allocation rules.
        """
        amount = msg.get("amount", 0.0)

        harvested = round(amount * 0.20, 2)
        retained = round(amount - harvested, 2)

        allocation = self._allocate(harvested)

        # Update ledger
        self.ledger.update_balance("income_total", amount)
        self.ledger.update_balance("harvested_total", harvested)
        self.ledger.update_balance("retained_total", retained)

        for bucket, value in allocation.items():
            self.ledger.update_balance(bucket, value)

        # Build output message
        msg.update({
            "harvested": harvested,
            "retained": retained,
            "allocation": allocation,
            "treasury_processed": True,
        })

        return msg

    # ---------------------------------------------------------
    # Allocation Logic
    # ---------------------------------------------------------
    def _allocate(self, harvested: float) -> Dict[str, float]:
        """
        Allocates harvested funds across TFSA/RRSP/RESP.
        Simple equal split for now.
        """
        split = round(harvested / 3, 2)

        return {
            "TFSA": split,
            "RRSP": split,
            "RESP": split,
        }


# ============================================================
# Entry Point
# ============================================================

async def main():
    agent = TreasuryAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
