"""
Policy Registry — Ardhanarishvara Motherboard
---------------------------------------------
Stores and retrieves policy functions.
"""

from typing import Callable, Dict, Optional


class PolicyRegistry:
    def __init__(self):
        self._policies: Dict[str, Callable] = {}

    def register(self, name: str, fn: Callable):
        self._policies[name] = fn

    def get(self, name: str) -> Optional[Callable]:
        return self._policies.get(name)

    def list(self):
        return list(self._policies.keys())
