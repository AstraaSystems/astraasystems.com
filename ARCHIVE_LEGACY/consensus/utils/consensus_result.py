"""
Consensus Result Structure
--------------------------
Represents the output of a consensus evaluation.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ConsensusResult:
    success: bool
    result: Any
    reason: str
    metadata: Optional[Dict[str, Any]] = None
