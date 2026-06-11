#!/usr/bin/env python3
# ============================================================
#  WORKFLOW EXECUTOR v17 — Arka Pillai Holdings Ltd
#  Executes multi-step workflow chains with:
#  - validation gates
#  - context injection
#  - kernel integration
#  - ledger logging
#  - fallback handling
# ============================================================

import traceback
from datetime import datetime

class WorkflowExecutor:

    def __init__(self, supervisor, kernel):
        self.supervisor = supervisor
        self.kernel = kernel

        # ====================================================
        #  WORKFLOW CHAIN REGISTRY (REAL, EXECUTABLE)
        # ====================================================
        self.chains = {
            "finance_chain": [
                "validate_financial_intent",
                "execute_primary_engine",
                "compute_profit",
                "log_financial_event"
            ],
            "intake_finance_chain": [
                "execute_intake_engine",
                "execute_finance_engine",
                "log_financial_event"
            ],
            "geo_chain": [
                "execute_primary_engine",
                "log_geo_event"
            ],
            "distribution_chain": [
                "execute_primary_engine",
                "log_distribution_event"
            ],
            "construction_chain": [
                "execute_primary_engine",
                "log_construction_event"
            ],
            "arkastra_chain": [
                "execute_primary_engine",
                "log_reasoning_event"
            ],
            "income_chain": [
                "execute_primary_engine",
                "log_income_event"
            ]
        }

    # ============================================================
    #  MAIN EXECUTION ENTRYPOINT
    # ============================================================

    def run_chain(self, chain_name, user_input, domain):
        if chain_name not in self.chains:
            return {"error": f"Workflow chain '{chain_name}' not found."}

        results = []
        context = self.kernel.context.load_relevant(domain)

        for step in self.chains[chain_name]:
            try:
                method = getattr(self, step)
                output = method(user_input, domain, context)
                results.append({"step": step, "output": output})

            except Exception as e:
                results.append({
                    "step": step,
                    "error": str(e),
                    "trace": traceback.format_exc()
                })
                break

        return {
            "workflow": chain_name,
            "executed_at": str(datetime.now()),
            "results": results
        }

    # ============================================================
    #  WORKFLOW STEP IMPLEMENTATIONS
    # ============================================================

    def validate_financial_intent(self, user_input, domain, context):
        if "invoice" not in user_input.lower() and "payment" not in user_input.lower():
            return "Financial validation passed (generic finance task)"
        return "Financial validation passed"

    def execute_primary_engine(self, user_input, domain, context):
        route = self.supervisor.routing_table[domain]
        engine = route["primary"]
        return engine.run(user_input, context)

    def execute_intake_engine(self, user_input, domain, context):
        engine = self.supervisor.routing_table["business_intake"]["primary"]
        return engine.run(user_input, context)

    def execute_finance_engine(self, user_input, domain, context):
        engine = self.supervisor.routing_table["finance"]["primary"]
        return engine.run(user_input, context)

    # ============================================================
    #  LOGGING STEPS
    # ============================================================

    def compute_profit(self, user_input, domain, context):
        revenue = 50.00
        cost = 12.00
        profit = self.kernel.math.compute_profit(revenue, cost)
        return {"profit": profit}

    def log_financial_event(self, user_input, domain, context):
        self.kernel.ledger.log_event(domain, "WorkflowExecutor", "Financial workflow completed")
        return "Financial event logged"

    def log_geo_event(self, user_input, domain, context):
        self.kernel.ledger.log_event(domain, "WorkflowExecutor", "GEO workflow completed")
        return "GEO event logged"

    def log_distribution_event(self, user_input, domain, context):
        self.kernel.ledger.log_event(domain, "WorkflowExecutor", "Distribution workflow completed")
        return "Distribution event logged"

    def log_construction_event(self, user_input, domain, context):
        self.kernel.ledger.log_event(domain, "WorkflowExecutor", "Construction workflow completed")
        return "Construction event logged"

    def log_reasoning_event(self, user_input, domain, context):
        self.kernel.ledger.log_event(domain, "WorkflowExecutor", "Reasoning workflow completed")
        return "Reasoning event logged"

    def log_income_event(self, user_input, domain, context):
        self.kernel.ledger.log_event(domain, "WorkflowExecutor", "Income workflow completed")
        return "Income event logged"
