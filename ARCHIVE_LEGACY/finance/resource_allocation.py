"""
Resource Allocation — Ardhanarishvara Motherboard
-------------------------------------------------
Unified, safe, backwards‑compatible resource allocation system for
ARKA, Astra, Aruhan, and future agents.

ARKA depends on:
- allocate(resources, demands)

This file guarantees that function exists and behaves safely.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


# ---------------------------------------------------------
# Structured Allocation Result
# ---------------------------------------------------------

@dataclass
class AllocationResult:
    status: str
    allocated: Dict[str, Any]
    unallocated: Dict[str, Any]
    reason: str
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Normalization Helpers
# ---------------------------------------------------------

def _normalize(resources: Any) -> Dict[str, Any]:
    """
    Normalize resources into a dictionary.
    """
    if resources is None:
        return {}
    if isinstance(resources, dict):
        return resources
    return {"value": resources}


def _normalize_demands(demands: Any) -> Dict[str, Any]:
    """
    Normalize demands into a dictionary.
    """
    if demands is None:
        return {}
    if isinstance(demands, dict):
        return demands
    return {"value": demands}


# ---------------------------------------------------------
# MAIN ENTRY POINT (ARKA depends on this)
# ---------------------------------------------------------

def allocate(resources: Any,
            demands: Any,
            strict: bool = False) -> AllocationResult:
    """
    Safe allocator that supports:
    - Scalar allocation: allocate("cpu", 4)
    - Dict allocation: allocate({"cpu": 8}, {"cpu": 4})
    - Never raises exceptions
    """

    # -----------------------------------------------------
    # CASE 1: Scalar allocation ("cpu", 4)
    # -----------------------------------------------------
    if isinstance(resources, str) and isinstance(demands, (int, float)):
        return AllocationResult(
            status="ok",
            allocated={resources: demands},
            unallocated={},
            reason="Scalar allocation completed",
            metadata={"mode": "scalar"}
        )

    # -----------------------------------------------------
    # CASE 2: Dict-based allocation
    # -----------------------------------------------------
    resources_norm = _normalize(resources)
    demands_norm = _normalize_demands(demands)

    if strict and (not resources_norm or not demands_norm):
        return AllocationResult(
            status="error",
            allocated={},
            unallocated=demands_norm,
            reason="Missing resources or demands in strict mode",
            metadata={"strict": True}
        )

    allocated = {}
    unallocated = {}

    for key, demand_value in demands_norm.items():
        resource_value = resources_norm.get(key, 0)

        # Numeric allocation
        if isinstance(resource_value, (int, float)) and isinstance(demand_value, (int, float)):
            if resource_value >= demand_value:
                allocated[key] = demand_value
            else:
                allocated[key] = resource_value
                unallocated[key] = demand_value - resource_value

        # Non-numeric fallback
        else:
            allocated[key] = resource_value
            unallocated[key] = demand_value

    return AllocationResult(
        status="ok",
        allocated=allocated,
        unallocated=unallocated,
        reason="Resource allocation completed",
        metadata={"strict": strict}
    )


# ---------------------------------------------------------
# Strict wrapper
# ---------------------------------------------------------

def allocate_strict(resources: Any, demands: Any) -> AllocationResult:
    return allocate(resources, demands, strict=True)
