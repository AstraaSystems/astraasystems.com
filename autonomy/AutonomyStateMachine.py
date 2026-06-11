#!/usr/bin/env python3
# ============================================================
#  AUTONOMY STATE MACHINE v17 — Arka Pillai Holdings Ltd
#  Controls:
#   - autonomy levels
#   - safety gates
#   - fallback escalation
#   - cooldown states
#   - self-restoration
#   - Supervisor override
# ============================================================

import time
from datetime import datetime

class AutonomyStateMachine:

    def __init__(self, kernel, supervisor):
        self.kernel = kernel
        self.supervisor = supervisor

        # ====================================================
        #  AUTONOMY LEVELS
        # ====================================================
        self.states = {
            "OBSERVATION": "System watches but does not act",
            "PARTIAL_AUTONOMY": "Engines act with Supervisor approval",
            "FULL_AUTONOMY": "Engines act independently",
            "REVOKED": "Autonomy disabled due to risk",
            "COOLDOWN": "Temporary lockout after failures",
            "SAFE_MODE": "Minimal operations only"
        }

        # Current state
        self.current_state = "OBSERVATION"

        # Failure tracking
        self.failure_count = 0
        self.last_failure_time = None

        # Cooldown timer
        self.cooldown_until = None

    # ============================================================
    #  STATE TRANSITION LOGIC
    # ============================================================

    def transition(self, new_state):
        old_state = self.current_state
        self.current_state = new_state

        self.kernel.ledger.log_event(
            "autonomy",
            "AutonomyStateMachine",
            {
                "old_state": old_state,
                "new_state": new_state,
                "timestamp": str(datetime.now())
            }
        )

        return {"from": old_state, "to": new_state}

    # ============================================================
    #  FAILURE HANDLING
    # ============================================================

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= 3:
            self.enter_cooldown()

    def enter_cooldown(self):
        self.cooldown_until = time.time() + 300  # 5 minutes
        self.transition("COOLDOWN")

    def check_cooldown(self):
        if self.current_state != "COOLDOWN":
            return False

        if time.time() >= self.cooldown_until:
            self.failure_count = 0
            self.transition("PARTIAL_AUTONOMY")
            return False

        return True

    # ============================================================
    #  AUTONOMY LEVEL CONTROLS
    # ============================================================

    def allow_action(self):
        """Determines if engines are allowed to act."""
        if self.current_state == "REVOKED":
            return False

        if self.current_state == "SAFE_MODE":
            return False

        if self.current_state == "COOLDOWN":
            return False

        return True

    def escalate_to_full(self):
        if self.current_state in ["PARTIAL_AUTONOMY", "OBSERVATION"]:
            return self.transition("FULL_AUTONOMY")

    def reduce_to_partial(self):
        if self.current_state == "FULL_AUTONOMY":
            return self.transition("PARTIAL_AUTONOMY")

    def revoke_autonomy(self):
        return self.transition("REVOKED")

    def restore_autonomy(self):
        return self.transition("PARTIAL_AUTONOMY")

    def enter_safe_mode(self):
        return self.transition("SAFE_MODE")

    # ============================================================
    #  SUPERVISOR OVERRIDE
    # ============================================================

    def supervisor_override(self, reason):
        self.kernel.ledger.log_event(
            "autonomy",
            "SupervisorOverride",
            {"reason": reason, "timestamp": str(datetime.now())}
        )
        return self.transition("PARTIAL_AUTONOMY")

    # ============================================================
    #  STATUS REPORT
    # ============================================================

    def status(self):
        return {
            "state": self.current_state,
            "description": self.states[self.current_state],
            "failures": self.failure_count,
            "cooldown_until": self.cooldown_until,
            "timestamp": str(datetime.now())
        }
