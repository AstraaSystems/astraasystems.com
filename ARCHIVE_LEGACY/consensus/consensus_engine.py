"""
ARKA Consensus Engine
---------------------
Provides multi-agent consensus mechanisms for:
- ARKA Core
- Astra
- Aruhan
- Multi-agent collaboration

Supports:
- Weighted voting
- Majority voting
- Arbitration
- Confidence scoring
"""

from typing import Dict, Any, List, Optional
from .strategies.majority_vote import majority_vote
from .strategies.weighted_vote import weighted_vote
from .utils.consensus_result import ConsensusResult


class ConsensusEngine:
    def __init__(self):
        self.strategies = {
            "majority": majority_vote,
            "weighted": weighted_vote
        }

    def evaluate(self, inputs: List[Dict[str, Any]], strategy: str = "majority") -> ConsensusResult:
        if strategy not in self.strategies:
            return ConsensusResult(
                success=False,
                result=None,
                reason=f"Unknown strategy '{strategy}'",
                metadata={"missing_strategy": True}
            )

        try:
            fn = self.strategies[strategy]
            result, reason, metadata = fn(inputs)
            return ConsensusResult(
                success=True,
                result=result,
                reason=reason,
                metadata=metadata
            )
        except Exception as e:
            return ConsensusResult(
                success=False,
                result=None,
                reason=f"Consensus error: {e}",
                metadata={"exception": True}
            )
