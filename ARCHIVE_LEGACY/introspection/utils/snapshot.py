"""
Snapshot Utility
----------------
Represents a full system telemetry snapshot.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Snapshot:
    timestamp: str
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    process: Dict[str, Any]
    platform: Dict[str, Any]
    health: str

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "cpu": self.cpu,
            "memory": self.memory,
            "disk": self.disk,
            "process": self.process,
            "platform": self.platform,
            "health": self.health
        }
