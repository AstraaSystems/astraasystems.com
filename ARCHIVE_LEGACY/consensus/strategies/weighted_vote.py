"""
Weighted Vote Strategy
----------------------
Each agent provides:
- value
- weight (confidence)
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict


def weighted_vote(inputs: List[Dict[str, Any]]) -> Tuple[Any, str, Dict[str, Any]]:
    scores = defaultdict(float)

    for entry in inputs:
        value = entry.get("value")
        weight = entry.get("weight", 1.0)
        scores[value] += weight

    if not scores:
        return None, "No inputs provided", {}

    result = max(scores.items(), key=lambda x: x[1])[0]
    return result, "Weighted vote completed", {"scores": dict(scores)}
