"""
State Result Structure
----------------------
Represents the output of a state transition or query.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class StateResult:
    state: str
    metadata: Dict[str, Any]
    reason: str
    success: bool = True
