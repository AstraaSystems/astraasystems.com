#!/usr/bin/env python3
# ============================================================
#  LEDGER v17 — Arka Pillai Holdings Ltd
#  Immutable financial event logging + reconciliation
# ============================================================

import json
import os
from datetime import datetime

class Ledger:

    def __init__(self):
        self.ledger_path = "/home/keshanth/ARKA/ardhanarishvara/ledger/transactions.json"
        os.makedirs("/home/keshanth/ARKA/ardhanarishvara/ledger/", exist_ok=True)

        if not os.path.exists(self.ledger_path):
            with open(self.ledger_path, "w") as f:
                json.dump([], f)

    # --------------------------------------------------------
    # Log a financial or operational event
    # --------------------------------------------------------
    def log_event(self, domain, engine, result):
        entry = {
            "timestamp": str(datetime.now()),
            "domain": domain,
            "engine": engine,
            "result": result
        }

        with open(self.ledger_path, "r") as f:
            data = json.load(f)

        data.append(entry)

        with open(self.ledger_path, "w") as f:
            json.dump(data, f, indent=4)

    # --------------------------------------------------------
    # Load ledger for audits
    # --------------------------------------------------------
    def load(self):
        with open(self.ledger_path, "r") as f:
            return json.load(f)
