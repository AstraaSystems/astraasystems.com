# ardhanarishvara/astra/astra_adapter.py

"""
ASTRA Adapter — Unified Integration Layer
Bridges ASTRA’s internal logic to the Ardhanarishvara motherboard.
All imports are mapped to the REAL motherboard APIs.
"""

# ---------------------------------------------------------
# AUTONOMY LAYER
# ---------------------------------------------------------

from ardhanarishvara.autonomy.goal_decomposition import decompose
from ardhanarishvara.autonomy.evaluation import evaluate
from ardhanarishvara.autonomy.policy_engine import enforce as apply_policy
from ardhanarishvara.autonomy.state_machine import transition as transition_state

# ---------------------------------------------------------
# SAFETY LAYER
# ---------------------------------------------------------

from ardhanarishvara.safety.safe_mode import safe_mode
from ardhanarishvara.safety.error_handling import handle as handle_error
from ardhanarishvara.safety.security_policies import check_access as security_check
from ardhanarishvara.safety.risk_framework import assess as assess_risk

# ---------------------------------------------------------
# COORDINATION LAYER
# ---------------------------------------------------------

from ardhanarishvara.coordination.consensus import sync_state as consensus

# ---------------------------------------------------------
# INFRASTRUCTURE LAYER
# ---------------------------------------------------------

from ardhanarishvara.infrastructure.memory_protocols import store_memory
from ardhanarishvara.infrastructure.task_routing import route_task
from ardhanarishvara.infrastructure.provisioning import provision
from ardhanarishvara.infrastructure.logging import log as log_event
from ardhanarishvara.infrastructure.telemetry import record as record_metric
from ardhanarishvara.infrastructure.health_monitor import check as health_check

# ---------------------------------------------------------
# FINANCE LAYER
# ---------------------------------------------------------

from ardhanarishvara.finance.budgeting import allocate_budget
from ardhanarishvara.finance.resource_allocation import allocate as allocate_resource


# ---------------------------------------------------------
# ASTRA ADAPTER CLASS
# ---------------------------------------------------------

class AstraAdapter:

    def decompose_goal(self, goal): return decompose(goal)
    def evaluate_goal(self, goal): return evaluate(goal)
    def apply_policy(self, policy, context=None): return apply_policy(policy, context)
    def transition_state(self, state, event): return transition_state(state, event)

    def enter_safe_mode(self, reason): return safe_mode(reason)
    def handle_error(self, error, context=None): return handle_error(error, context)
    def security_check(self, user, action): return security_check(user, action)
    def assess_risk(self, event, context=None): return assess_risk(event, context)

    def consensus(self, state, peers=None): return consensus(state, peers)

    def store_memory(self, key, value): return store_memory(key, value)
    def route_task(self, task): return route_task(task)
    def provision(self, resource): return provision(resource)

    def log_event(self, message, level="info"): return log_event(message, level)
    def record_metric(self, event, data=None): return record_metric(event, data)
    def health_check(self, component="astra"): return health_check(component)

    def apply_budgeting(self, amount): return allocate_budget(amount)
    def apply_resource_allocation(self, resource, amount): return allocate_resource(resource, amount)
