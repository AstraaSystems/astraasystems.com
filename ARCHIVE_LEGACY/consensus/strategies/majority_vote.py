"""
Majority Vote Strategy
----------------------
Each agent gets one vote.
"""

from typing import List, Dict, Any, Tuple
from collections import Counter


def majority_vote(inputs: List[Dict[str, Any]]) -> Tuple[Any, str, Dict[str, Any]]:
    votes = [i["value"] for i in inputs]
    counter = Counter(votes)

    if not counter:
        return None, "No inputs provided", {}

    result, count = counter.most_common(1)[0]
    return result, "Majority vote completed", {"counts": dict(counter)}
