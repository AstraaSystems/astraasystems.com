import os
import sys
import sqlite3
import re
import json
import requests
from datetime import datetime

DB_PATH = "arka_core.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lifecycle_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            type TEXT,
            content TEXT,
            target_date TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_lifecycle(content, entry_type, target_date=None, status="active"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lifecycle_store (timestamp, type, content, target_date, status) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), entry_type, content, target_date, status)
    )
    conn.commit()
    conn.close()

def search_local_records(query_term):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT type, content, timestamp, status FROM lifecycle_store WHERE content LIKE ?", (f"%{query_term}%",))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fallback_web_search(query):
    """Safe, direct extraction wrapper using DuckDuckGo HTML/Lite interface"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers, timeout=6)
        if res.status_code == 200:
            # Quick structural extraction of text snippets
            links = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', res.text, re.DOTALL)
            if links:
                return [re.sub(r'<[^>]+>', '', l).strip() for l in links[:3]]
    except Exception:
        pass
    return ["Unable to pull live web text streams. Check local infrastructure connectivity."]

class ArkaTerminalCEO:
    def __init__(self):
        init_db()
        self.session_state = "READY"
        self.staged_transaction = None

    def process_input(self, text):
        raw = text.strip()
        low = raw.lower()

        if not raw:
            return "Listening. State your directive, Chief."

        # --- TRANSACTION LOCK STATE ---
        if self.session_state == "WAITING_FOR_AUTH":
            if low in ["yes", "approve", "confirm", "y"]:
                return self.execute_staged_booking()
            else:
                self.session_state = "READY"
                self.staged_transaction = None
                return "[TRANSACTION ABORTED] Order canceled. Arka core reverted to READY state."

        # --- ROUTING LOGIC: FLIGHTS & BOOKING ---
        if "flight" in low or "ticket" in low or "book" in low:
            if "price" in low or "find" in low or "search" in low:
                # Extract locations using simple patterns for interface resilience
                match = re.search(r"to\s+([A-Za-z\s]+)", low)
                dest = match.group(1).strip() if match else "your requested destination"
                
                # Mocking API aggregation pass for demonstration
                flight_options = {
                    "destination": dest,
                    "price_cad": 640 if "london" in low else 420,
                    "carrier": "Air Canada" if "london" in low else "WestJet",
                    "status": "STAGED_HOLD"
                }
                
                self.staged_transaction = flight_options
                self.session_state = "WAITING_FOR_AUTH"
                
                return (
                    f"\n[ARKA FLIGHT DISCOVERY]\n"
                    f"I found an optimal matching route to {dest.title()}:\n"
                    f" - Carrier: {flight_options['carrier']}\n"
                    f" - Total Cost: ${flight_options['price_cad']} CAD (All taxes incl.)\n"
                    f" - Policy: 24h Free cancellation held locally.\n\n"
                    f"⚠️ [AUTHORIZATION REQUIRED]: Do you authorize me to settle payment and confirm this ticket? (Type YES to execute / ANY other key to cancel)"
                )

        # --- ROUTING LOGIC: MEMORIES ---
        if "remember that" in low or "save memory" in low:
            clean_memory = re.sub(r"^(remember that|save memory)\s*", "", raw, flags=re.I)
            log_lifecycle(clean_memory, "memory", status="pending_approval")
            return f"[MEMORY LOGGED] Draft saved to local stack: \"{clean_memory}\". Staged under Pending Approvals."

        if "what do you remember about" in low or "recall" in low:
            term = low.replace("what do you remember about", "").replace("recall", "").strip("? .")
            records = search_local_records(term)
            if not records:
                return f"I ran a local vector scan for '{term}' but found no verified parameters."
            
            output = [f"Here is what I have indexed regarding '{term}':"]
            for r in records:
                output.append(f" • [{r[0].upper()} - Status: {r[3]}] {r[1]}")
            return "\n".join(output)

        # --- ROUTING LOGIC: PLANS ---
        if "plan" in low or "schedule" in low:
            if "save" in low or "new" in low or "add" in low:
                clean_plan = re.sub(r"^(save plan|new plan|add plan|plan)\s*", "", raw, flags=re.I)
                log_lifecycle(clean_plan, "plan", status="active")
                return f"[STRATEGIC PLAN LOGGED] Added to operational pipeline: \"{clean_plan}\""

        # --- ROUTING LOGIC: WEB SEARCH ---
        if "search the web for" in low or "google" in low or "web search" in low:
            query = re.sub(r"^(search the web for|google|web search)\s*", "", raw, flags=re.I)
            web_data = fallback_web_search(query)
            output = [f"[LIVE WEB LOOKUP RESULTS FOR: {query}]"]
            for idx, snippet in enumerate(web_data, 1):
                output.append(f" {idx}. {snippet}")
            return "\n".join(output)

        # --- DEFAULT REASONING FALLBACK ---
        return (
            f"Command received. I understand your context regarding: \"{raw}\".\n"
            f"To bind this dynamically, route via standard verbs:\n"
            f" - 'Remember that [fact]'\n"
            f" - 'Plan [milestone]'\n"
            f" - 'Search the web for [topic]'\n"
            f" - 'Find flight prices to [city]'"
        )

    def execute_staged_booking(self):
        tx = self.staged_transaction
        self.session_state = "READY"
        self.staged_transaction = None
        
        # Simulating automated token payload settlement
        return (
            f"\n[✔️ TRANSACTION SECURED & SETTLED]\n"
            f"Authentication Key validated against environment.\n"
            f"Ticket issued to {tx['destination'].title()} via {tx['carrier']}.\n"
            f"Receipt logged under local accounting engine ledger. Total debited: ${tx['price_cad']} CAD."
        )

def main():
    ceo = ArkaTerminalCEO()
    print("\n" + "="*60)
    print(" ARKA AI EXECUTIVE CORE ENGINE v0.5.0")
    print(" Operating Mode: Local System Native Interface")
    print(" System Status: ONLINE & READY")
    print("="*60)
    print("Speak to Arka in plain text. Type 'exit' to cleanly close runtime.\n")

    while True:
        try:
            user_input = input("User >> ")
            if user_input.strip().lower() == 'exit':
                print("[INFO] Terminating session loop. Core engine sleeping.")
                break
            response = ceo.process_input(user_input)
            print(f"\nArka >> {response}\n")
            print("-" * 50)
        except KeyboardInterrupt:
            print("\n[INFO] Safe exit signal caught. Closing.")
            break
        except Exception as e:
            print(f"\nArka Exception >> Runtime error encountered: {str(e)}\n")

if __name__ == "__main__":
    main()
