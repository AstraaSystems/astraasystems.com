import json
from pathlib import Path
from datetime import datetime, timezone

class JsonLedger:
    def __init__(self, filename="aruhan_ledger.jsonl"):
        self.path = Path(filename).resolve()
        self.path.touch(exist_ok=True)

    def append(self, record: dict):
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def read_all(self):
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
