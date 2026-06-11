"""
Multi‑Agent Coordination — Ardhanarishvara Motherboard
------------------------------------------------------
Provides a unified multi‑agent coordination interface for ARKA, Astra,
Aruhan, and future agents.

ARKA depends on:
- ArkaMultiAgentCoordinator
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class CoordinationResult:
    status: str
    agents: List[str]
    action: str
    metadata: Optional[Dict[str, Any]] = None


class ArkaMultiAgentCoordinator:
    """
    Minimal, safe, backwards‑compatible coordinator.
    """

    def __init__(self, agents: Optional[List[str]] = None):
        self.agents = agents or []

    def broadcast(self, action: str, payload: Optional[Dict[str, Any]] = None) -> CoordinationResult:
        return CoordinationResult(
            status="ok",
            agents=self.agents,
            action=action,
            metadata={"payload": payload}
        )

    def add_agent(self, agent: str):
        if agent not in self.agents:
            self.agents.append(agent)

    def remove_agent(self, agent: str):
        if agent in self.agents:
            self.agents.remove(agent)
