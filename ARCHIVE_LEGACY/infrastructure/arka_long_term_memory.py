"""
Centralized Long-Term Memory Module
Shared by ARKA, ASTRA, and ARUHAN
Located in: ardhanarishvara/infrastructure/
"""

import json
import os
from datetime import datetime


class LongTermMemory:
    def __init__(self, storage_path="ardhanarishvara/memory/data/semantic.jsonl"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def store(self, key: str, value: str):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "key": key,
            "value": value
        }
        with open(self.storage_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return {"success": True, "stored": entry}

    def retrieve(self, key: str):
        if not os.path.exists(self.storage_path):
            return None

        with open(self.storage_path, "r") as f:
            for line in f:
                entry = json.loads(line)
                if entry["key"] == key:
                    return entry
        return None
