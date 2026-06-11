#!/usr/bin/env python3
# ============================================================
# SYSTEM: ARDHANARISHVARA EXECUTION LAYER
# MODULE: IBKR EXECUTION HUB (Unified with Lux Harvest Routing)
# ENGINE: ib_async (Asynchronous Event Loop Gateway)
# ============================================================

import asyncio
import logging
import time
import pandas as pd
from ib_async import IB, Stock, LimitOrder, util

class IBKRExecutionHub:
    def __init__(self, ipc, host="127.0.0.1", port=7497, client_id=1):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ipc = ipc

        self.ib = IB()

        self.trading_account_id = None
        self.tfsa_account_id = None

        # Profit tracking baseline
        self.last_cash_value = None

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
        self.logger = logging.getLogger("IBKR_Bridge")

    # ============================================================
    # INITIALIZE GATEWAY
    # ============================================================
    async def initialize_gateway(self):
        self.logger.info(f"Connecting to IB Gateway at {self.host}:{self.port}...")
        await self.ib.connectAsync(self.host, self.port, clientId=self.client_id)

        managed_accounts = self.ib.managedAccounts()
        self.logger.info(f"Connected. Sub-accounts discovered: {managed_accounts}")

        self.trading_account_id = managed_accounts[0]
        if len(managed_accounts) > 1:
            self.tfsa_account_id = managed_accounts[1]

    # ============================================================
    # STREAMING MARKET DATA LOOP
    # ============================================================
    async def streaming_market_data_handler(self, contract: Stock):
        self.logger.info(f"Requesting real-time data for: {contract.symbol}")

        self.ib.reqMarketDataType(1)
        ticker = self.ib.reqMktData(contract)

        try:
            while True:
                await asyncio.sleep(1.0)

                if ticker.last is not None:
                    price = ticker.last

                    # Example breakout trigger
                    if price > 155.0:
                        self.logger.warning(
                            f"Breakout detected: {contract.symbol} at ${price:.2f}"
                        )
                        asyncio.create_task(
                            self.execute_autonomous_trade(contract, "BUY", 100, price)
                        )
                        break

        except asyncio.CancelledError:
            self.logger.info(f"Market stream for {contract.symbol} terminated.")

    # ============================================================
    # ORDER EXECUTION
    # ============================================================
    async def execute_autonomous_trade(self, contract, action, qty, limit_price):
        self.logger.info(f"Assembling {action} order for {qty} units of {contract.symbol}")

        order = LimitOrder(action, qty, limit_price)
        order.account = self.trading_account_id
        order.transmit = True

        await self.ib.qualifyContractsAsync(contract)

        self.logger.info(f"Transmitting order to account [{self.trading_account_id}]...")
        trade = self.ib.placeOrder(contract, order)

        while not trade.isDone():
            await asyncio.sleep(0.5)

        self.logger.info(f"Order filled. Status: {trade.orderStatus.status}")

        if trade.orderStatus.status == "Filled":
            await self.reconcile_and_harvest_revenues()

    # ============================================================
    # PROFIT RECONCILIATION + 20% HARVEST
    # ============================================================
    async def reconcile_and_harvest_revenues(self):
        self.logger.info("Running treasury audit...")

        summary = await self.ib.accountSummaryAsync(self.trading_account_id)
        df = util.df(summary)

        cash_row = df[df['tag'] == 'TotalCashValue']
        if cash_row.empty:
            self.logger.warning("TotalCashValue not found.")
            return

        current_cash = float(cash_row.iloc[0]['value'])
        self.logger.info(f"Settled Cash: ${current_cash:,.2f}")

        # First run: initialize baseline
        if self.last_cash_value is None:
            self.last_cash_value = current_cash
            self.logger.info("Baseline initialized. No harvest this cycle.")
            return

        # Calculate profit delta
        profit = current_cash - self.last_cash_value
        if profit <= 0:
            self.logger.info("No positive profit. Harvest skipped.")
            self.last_cash_value = current_cash
            return

        # Harvest 20%
        harvest_amount = profit * 0.20
        self.logger.info(f"Profit detected: ${profit:,.2f}")
        self.logger.info(f"Harvesting 20%: ${harvest_amount:,.2f}")

        # Update baseline
        self.last_cash_value = current_cash

        # Route to Lux
        await self.route_harvest_to_lux(harvest_amount)

    # ============================================================
    # ROUTE HARVEST TO LUX
    # ============================================================
    async def route_harvest_to_lux(self, amount: float):
        self.logger.info(f"Routing harvested profit to Lux: ${amount:,.2f}")

        payload = {
            "type": "harvest",
            "amount": amount,
            "timestamp": time.time(),
            "source": "Astraa.IncomeEngine"
        }

        self.ipc.publish("lux.intake", payload)

        self.logger.info("Harvest successfully transmitted to Lux.")

    # ============================================================
    # CLEAN SHUTDOWN
    # ============================================================
    async def shutdown(self):
        self.logger.info("Disconnecting from IBKR...")
        self.ib.disconnect()


# ============================================================
# MAIN ENTRYPOINT
# ============================================================
async def main(ipc):
    hub = IBKRExecutionHub(ipc)
    await hub.initialize_gateway()

    target_equity = Stock(symbol="VFV", exchange="SMART", currency="CAD")

    stream_task = asyncio.create_task(
        hub.streaming_market_data_handler(target_equity)
    )

    await asyncio.gather(stream_task)
