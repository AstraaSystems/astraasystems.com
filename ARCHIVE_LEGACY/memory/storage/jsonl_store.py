"""
JSONL Storage Engine
--------------------
Simple, safe, append-only persistent storage.
"""

import json
import os
from typing import Dict, Any, List


class JSONLStore:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            open(path, "w").close()

    def append(self, record: Dict[str, Any]):
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def read_all(self) -> List[Dict[str, Any]]:
        records = []
        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def trim(self, max_records: int):
        records = self.read_all()
        if len(records) <= max_records:
            return
        trimmed = records[-max_records:]
        with open(self.path, "w") as f:
            for r in trimmed:
                f.write(json.dumps(r) + "\n")
