"""
Agent Registry
--------------
Stores agent handlers for task routing.
"""

from typing import Callable, Dict, Optional
from .aruhan_agent import AruhanAgent


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, Callable] = {}

    def register(self, name: str, handler: Callable):
        self._agents[name] = handler

    def get(self, name: str) -> Optional[Callable]:
        return self._agents.get(name)

    def list(self):
        return list(self._agents.keys())

"aruhan": AruhanAgent,
