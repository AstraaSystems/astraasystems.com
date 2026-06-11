"""
ARKA Extended State Machine
---------------------------
Provides lifecycle control for:
- ARKA Core
- Astra
- Aruhan
- Multi-agent orchestration

States:
- idle
- running
- paused
- waiting
- blocked
- error
- recovering
- shutdown
"""

from typing import Dict, Any
from .utils.state_result import StateResult
from .transitions.transition_rules import VALID_TRANSITIONS


class StateMachine:
    def __init__(self):
        self.state = "idle"
        self.metadata: Dict[str, Any] = {}

    def get_state(self):
        return StateResult(
            state=self.state,
            metadata=self.metadata,
            reason="State retrieved"
        )

    def can_transition(self, new_state: str) -> bool:
        return new_state in VALID_TRANSITIONS.get(self.state, [])

    def transition(self, new_state: str, metadata: Dict[str, Any] = None) -> StateResult:
        if not self.can_transition(new_state):
            return StateResult(
                state=self.state,
                metadata=self.metadata,
                reason=f"Invalid transition: {self.state} → {new_state}",
                success=False
            )

        self.state = new_state
        if metadata:
            self.metadata.update(metadata)

        return StateResult(
            state=self.state,
            metadata=self.metadata,
            reason=f"Transitioned to {new_state}",
            success=True
        )

    def reset(self):
        self.state = "idle"
        self.metadata = {}
        return StateResult(
            state=self.state,
            metadata=self.metadata,
            reason="State machine reset",
            success=True
        )

