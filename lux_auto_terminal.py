import asyncio

# --- MODERN PYTHON EVENT LOOP PATCH ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# --- SYSTEM IMPORTS ---
import os
import json
import time
import uuid
import math
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from ib_insync import IB, Stock, LimitOrder

# --- CONFIGURATION & PATHS ---
BASE_DIR = Path(__file__).resolve().parent
LUX_DIR = BASE_DIR / "lux"
LUX_DIR.mkdir(parents=True, exist_ok=True)

BASKETS_FILE = LUX_DIR / "agent_baskets.jsonl"
OUTCOMES_FILE = LUX_DIR / "manual_trade_outcomes.jsonl"
PROPOSALS_FILE = LUX_DIR / "trade_proposals.jsonl"

BASE_LINE = 1000.0

# --- IBKR CONNECTION SETTINGS ---
IBKR_HOST = "127.0.0.1"
IBKR_PORT = 7497  # Default for TWS Paper Trading

@dataclass
class AgentBasket:
    agent_id: str
    client_id: int
    status: str
    allocated_capital: float
    current_balance: float
    date_spawned: str

class PoolManager:
    def __init__(self):
        self.baskets_file = BASKETS_FILE
        if not self.baskets_file.exists():
            print("[INIT] No active trading pods detected. Spawning initial test portfolio...")
        else:
            print("[INIT] Active tracking files loaded successfully.")

    def spawn_new_agent(self, status="simulated"):
        """Creates a new tracking agent and persists it to the storage layer."""
        client_id = 1
        if self.baskets_file.exists():
            with open(self.baskets_file, "r") as f:
                client_id = len([line for line in f if line.strip()]) + 1

        new_agent = AgentBasket(
            agent_id=f"lux_agent_{client_id:02d}",
            client_id=client_id,
            status=status,
            allocated_capital=BASE_LINE,
            current_balance=BASE_LINE,
            date_spawned=datetime.now().strftime("%Y-%m-%d")
        )

        with open(self.baskets_file, "a") as f:
            f.write(json.dumps(asdict(new_agent)) + "\n")

        print(f"[POOL] Spawned {new_agent.agent_id} ({status.upper()}) | Client ID: {client_id}")
        return new_agent

    def print_active_loops(self):
        """Displays status summaries for all current tracking agents."""
        if not self.baskets_file.exists():
            return
        print("\n[ACTIVE RECOVERY LOOPS]")
        with open(self.baskets_file, "r") as f:
            for line in f:
                if line.strip():
                    a = json.loads(line)
                    print(f"- {a['agent_id']} ({a['status'].upper()}): Dynamic Fuel Line: ${a['current_balance']:.2f}")

    def execute_queued_proposals(self):
        """Parses active trade proposals, executes simulated OR live paper fills, and logs outcomes."""
        if not PROPOSALS_FILE.exists():
            print("[EXEC] No proposals file found.")
            return
            
        with open(PROPOSALS_FILE, "r") as f:
            lines = f.readlines()
            
        if not lines:
            print("[EXEC] No active proposals in queue.")
            return
            
        # Clear queue file now that processing has begun
        open(PROPOSALS_FILE, "w").close()
        
        if not BASKETS_FILE.exists():
            print("[WARN] No agent baskets found to apply trades against.")
            return
            
        with open(BASKETS_FILE, "r") as f:
            agents = [json.loads(line) for line in f if line.strip()]
            
        for line in lines:
            if not line.strip():
                continue
            proposal = json.loads(line)
            agent_id = proposal["agent_id"]
            ticker = proposal["ticker"]
            action = proposal["action"]
            qty = proposal["quantity"]
            
            print(f"\n[ORDER] Agent {agent_id} matching proposal [{ticker} | {action} | {qty}]")
            
            agent = next((a for a in agents if a["agent_id"] == agent_id), None)
            if not agent:
                print(f"[WARN] Agent {agent_id} not found in tracking files.")
                continue
                
            # --- ROUTE 1: SIMULATED EXECUTION ---
            if agent["status"].lower() == "simulated":
                mock_price = 150.00  
                total_cost = mock_price * qty
                
                if agent["current_balance"] >= total_cost:
                    agent["current_balance"] -= total_cost
                    print(f"[SIM-EXEC] Filled {qty} shares of {ticker} at mock price ${mock_price:.2f}. Cost: ${total_cost:.2f}")
                    self._log_outcome(agent_id, ticker, action, qty, mock_price, total_cost)
                else:
                    print(f"[ERR] Insufficient dynamic fuel. Required: ${total_cost}, Available: ${agent['current_balance']}")
            
            # --- ROUTE 2: LIVE MULTI-HOUR IBKR PAPER EXECUTION ---
            elif agent["status"].lower() == "paper":
                print(f"[CONN] Initializing live socket connection to IBKR for {agent_id}...")
                ib = IB()
                try:
                    ib.connect(IBKR_HOST, IBKR_PORT, clientId=agent["client_id"])
                    ib.reqMarketDataType(3)  
                    
                    contract = Stock(ticker, 'SMART', 'USD')
                    ib.qualifyContracts(contract)
                    
                    [ticker_data] = ib.reqTickers(contract)
                    market_price = ticker_data.marketPrice()
                    
                    if math.isnan(market_price) or market_price <= 0:
                        market_price = ticker_data.close or ticker_data.last or 150.0
                    
                    if action.upper() == "BUY":
                        limit_price = round(market_price * 1.02, 2)
                    else:
                        limit_price = round(market_price * 0.98, 2)
                        
                    print(f"[LIVE-ROUTE] Transmitting All-Hours Limit Order: {action} {qty} {ticker} capped at ${limit_price:.2f}")
                    
                    order = LimitOrder(action, qty, limit_price)
                    order.outsideRth = True  # Passport flag to cross regular trading hours
                    order.tif = 'GTC'        # Explicitly override TWS preset to keep order alive overnight
                    
                    trade = ib.placeOrder(contract, order)
                    ib.sleep(2.0)  
                    
                    # Check true real-time book status after the sleep interval
                    current_status = trade.orderStatus.status.lower()
                    
                    if trade.isDone() or current_status in ['submitted', 'presubmitted']:
                        execution_price = trade.orderStatus.avgFillPrice or market_price
                        total_cost = execution_price * qty
                        
                        if agent["current_balance"] >= total_cost:
                            agent["current_balance"] -= total_cost
                            if current_status in ['submitted', 'presubmitted']:
                                print(f"[LIVE-BOOKED] Order successfully placed in overnight queue. Status: {trade.orderStatus.status}")
                            else:
                                print(f"[LIVE-FILL] Successfully filled at market price: ${execution_price:.2f}. Total Cost: ${total_cost:.2f}")
                            self._log_outcome(agent_id, ticker, action, qty, execution_price, total_cost)
                        else:
                            print(f"[ERR] Post-trade alert: Total execution cost ${total_cost:.2f} exceeded agent balance.")
                    else:
                        print(f"[WARN] Order was rejected or cancelled by exchange. Current state: {trade.orderStatus.status}")
                        
                    ib.disconnect()
                except Exception as e:
                    print(f"[NETWORK-ERR] Connection to IBKR TWS/Gateway failed: {e}")
                    print("[FALLBACK] Aborting paper transaction.")
                    
        # Update state persistence layer
        with open(BASKETS_FILE, "w") as f:
            for a in agents:
                f.write(json.dumps(a) + "\n")
        print("[LOG] Agent balance sheets synchronized successfully.")

    def _log_outcome(self, agent_id, ticker, action, qty, price, total_value):
        """Helper to append trade execution telemetry directly to local storage."""
        outcome = {
            "outcome_id": str(uuid.uuid4())[:8],
            "agent_id": agent_id,
            "ticker": ticker,
            "action": action,
            "quantity": qty,
            "price": price,
            "total_value": total_value,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(OUTCOMES_FILE, "a") as out_f:
            out_f.write(json.dumps(outcome) + "\n")
        print(f"[LOG] Outcome committed to {OUTCOMES_FILE.name}")


if __name__ == "__main__":
    manager = PoolManager()
    
    registered_statuses = []
    if BASKETS_FILE.exists() and os.path.getsize(BASKETS_FILE) > 0:
        with open(BASKETS_FILE, "r") as f:
            for line in f:
                if line.strip():
                    registered_statuses.append(json.loads(line).get("status", "").lower())
                    
    if "simulated" not in registered_statuses:
        manager.spawn_new_agent(status="simulated")
        
    if "paper" not in registered_statuses:
        manager.spawn_new_agent(status="paper")
        
    manager.print_active_loops()
    
    print("\n[TEST] Queueing parallel setups to verify both routing channels...")
    proposals = [
        {"proposal_id": f"sim_{str(uuid.uuid4())[:4]}", "agent_id": "lux_agent_01", "ticker": "AAPL", "action": "BUY", "quantity": 1},
        {"proposal_id": f"live_{str(uuid.uuid4())[:4]}", "agent_id": "lux_agent_02", "ticker": "TSLA", "action": "BUY", "quantity": 1}
    ]
    
    with open(PROPOSALS_FILE, "a") as f:
        for prop in proposals:
            f.write(json.dumps(prop) + "\n")
            
    print(f"[TEST] {len(proposals)} test profiles appended to execution queue.")

    print("[EXEC] Processing active queues...")
    manager.execute_queued_proposals()
