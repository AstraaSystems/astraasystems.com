"""
Task Result Structure
---------------------
Represents the output of a routed task.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class TaskResult:
    agent: str
    success: bool
    result: Any
    reason: str
    metadata: Optional[Dict[str, Any]] = None
