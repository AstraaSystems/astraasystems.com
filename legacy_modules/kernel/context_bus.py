#!/usr/bin/env python3
# ============================================================
#  CONTEXT BUS v17 — Arka Pillai Holdings Ltd
#  Handles: filtering, summarization, JIT loading, offloading
# ============================================================

import json
import os
from datetime import datetime

class ContextBus:

    def __init__(self):
        self.context_dir = "/home/keshanth/ARKA/ardhanarishvara/context/"
        os.makedirs(self.context_dir, exist_ok=True)

    # --------------------------------------------------------
    # Load only relevant context for a domain
    # --------------------------------------------------------
    def load_relevant(self, domain: str) -> dict:
        path = f"{self.context_dir}{domain}.json"
        if not os.path.exists(path):
            return {}

        with open(path, "r") as f:
            data = json.load(f)

        # Summarize if too large
        if len(json.dumps(data)) > 50000:
            data = self.summarize(data)

        return data

    # --------------------------------------------------------
    # Save context back to disk
    # --------------------------------------------------------
    def save(self, domain: str, context: dict):
        path = f"{self.context_dir}{domain}.json"
        with open(path, "w") as f:
            json.dump(context, f, indent=4)

    # --------------------------------------------------------
    # Summarization logic
    # --------------------------------------------------------
    def summarize(self, data: dict) -> dict:
        summary = {
            "summary_generated": str(datetime.now()),
            "keys": list(data.keys())[:10],
            "notes": "Context auto‑summarized by ContextBus v17"
        }
        return summary
