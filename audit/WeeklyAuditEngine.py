#!/usr/bin/env python3
# ============================================================
#  WEEKLY AUDIT ENGINE v17 — Arka Pillai Holdings Ltd
#  Performs:
#   - financial audit
#   - engine reliability audit
#   - routing audit
#   - workflow audit
#   - context audit
#   - divergence audit
#   - optimization audit
#   - autonomy verification
# ============================================================

import json
import os
from datetime import datetime

class WeeklyAuditEngine:

    def __init__(self, supervisor, kernel, workflow_executor, profit_engine, autonomy_machine):
        self.supervisor = supervisor
        self.kernel = kernel
        self.workflow_executor = workflow_executor
        self.profit_engine = profit_engine
        self.autonomy = autonomy_machine

        self.audit_path = "/home/keshanth/ARKA/ardhanarishvara/audit/weekly_history.json"
        os.makedirs("/home/keshanth/ARKA/ardhanarishvara/audit/", exist_ok=True)

        if not os.path.exists(self.audit_path):
            with open(self.audit_path, "w") as f:
                json.dump({"history": []}, f, indent=4)

    # ============================================================
    #  MAIN ENTRYPOINT
    # ============================================================

    def run(self):
        audit = {
            "timestamp": str(datetime.now()),
            "financial_audit": self.financial_audit(),
            "engine_reliability": self.engine_reliability_audit(),
            "routing_audit": self.routing_audit(),
            "workflow_audit": self.workflow_audit(),
            "context_audit": self.context_audit(),
            "divergence_audit": self.divergence_audit(),
            "optimization_recommendations": self.optimization_audit(),
            "autonomy_verification": self.autonomy_verification()
        }

        # Save audit
        with open(self.audit_path, "r") as f:
            data = json.load(f)

        data["history"].append(audit)

        with open(self.audit_path, "w") as f:
            json.dump(data, f, indent=4)

        return audit

    # ============================================================
    # 1. FINANCIAL AUDIT
    # ============================================================

    def financial_audit(self):
        ledger = self.kernel.ledger.load()
        issues = []

        for entry in ledger:
            result = entry.get("result", {})
            if "revenue_generated" not in result and "cycle_revenue" not in result:
                issues.append({
                    "timestamp": entry["timestamp"],
                    "engine": entry["engine"],
                    "issue": "Missing revenue field"
                })

        snapshot = self.profit_engine.aggregate()

        return {
            "ledger_entries": len(ledger),
            "profit_snapshot": snapshot,
            "issues": issues
        }

    # ============================================================
    # 2. ENGINE RELIABILITY AUDIT
    # ============================================================

    def engine_reliability_audit(self):
        failures = self.kernel.circuit.failures
        reliability = {}

        for engine, count in failures.items():
            reliability[engine] = {
                "failures": count,
                "status": "unstable" if count >= 3 else "stable"
            }

        return reliability

    # ============================================================
    # 3. ROUTING AUDIT
    # ============================================================

    def routing_audit(self):
        issues = []

        for domain, route in self.supervisor.routing_table.items():
            primary = route["primary"].__class__.__name__
            fallback = route["fallback"].__class__.__name__

            if primary == fallback:
                issues.append(f"Domain '{domain}' has identical primary and fallback engines")

        return issues

    # ============================================================
    # 4. WORKFLOW AUDIT
    # ============================================================

    def workflow_audit(self):
        issues = []

        for chain_name, steps in self.workflow_executor.chains.items():
            if len(steps) == 0:
                issues.append(f"Workflow '{chain_name}' has no steps")
            if len(steps) > 8:
                issues.append(f"Workflow '{chain_name}' is too long ({len(steps)} steps)")

        return issues

    # ============================================================
    # 5. CONTEXT AUDIT
    # ============================================================

    def context_audit(self):
        context_dir = "/home/keshanth/ARKA/ardhanarishvara/context/"
        issues = []

        for file in os.listdir(context_dir):
            path = os.path.join(context_dir, file)
            size = os.path.getsize(path)

            if size > 100000:  # 100 KB
                issues.append(f"Context file '{file}' is too large ({size} bytes)")

        return issues

    # ============================================================
    # 6. DIVERGENCE AUDIT
    # ============================================================

    def divergence_audit(self):
        return self.profit_engine.detect_divergence()

    # ============================================================
    # 7. OPTIMIZATION AUDIT
    # ============================================================

    def optimization_audit(self):
        recommendations = []

        # Engines with high failure rates
        for engine, count in self.kernel.circuit.failures.items():
            if count >= 3:
                recommendations.append(f"Engine '{engine}' should be reviewed or retrained")

        # Workflows too long
        for chain_name, steps in self.workflow_executor.chains.items():
            if len(steps) > 6:
                recommendations.append(f"Workflow '{chain_name}' should be optimized")

        return recommendations

    # ============================================================
    # 8. AUTONOMY VERIFICATION
    # ============================================================

    def autonomy_verification(self):
        state = self.autonomy.status()

        if state["state"] == "REVOKED":
            return {"status": "critical", "message": "Autonomy revoked — manual review required"}

        if state["state"] == "COOLDOWN":
            return {"status": "warning", "message": "System in cooldown — monitor stability"}

        return {"status": "ok", "message": "Autonomy stable"}
