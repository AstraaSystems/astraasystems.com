#!/usr/bin/env python3
# ============================================================
#  NIGHTLY REFLECTION ENGINE v17 — Arka Pillai Holdings Ltd
#  Handles:
#   - daily summaries
#   - failure pattern detection
#   - routing optimization
#   - workflow refinement
#   - context cleanup
#   - profit snapshot update
#   - micro-optimization
#   - autonomy adjustments
# ============================================================

import json
import os
from datetime import datetime

class NightlyReflectionEngine:

    def __init__(self, supervisor, kernel, workflow_executor, profit_engine, autonomy_machine):
        self.supervisor = supervisor
        self.kernel = kernel
        self.workflow_executor = workflow_executor
        self.profit_engine = profit_engine
        self.autonomy = autonomy_machine

        self.reflection_path = "/home/keshanth/ARKA/ardhanarishvara/reflection/nightly_history.json"
        os.makedirs("/home/keshanth/ARKA/ardhanarishvara/reflection/", exist_ok=True)

        if not os.path.exists(self.reflection_path):
            with open(self.reflection_path, "w") as f:
                json.dump({"history": []}, f, indent=4)

    # ============================================================
    #  MAIN ENTRYPOINT
    # ============================================================

    def run(self):
        summary = {
            "timestamp": str(datetime.now()),
            "daily_summary": self.generate_daily_summary(),
            "failure_patterns": self.detect_failure_patterns(),
            "routing_updates": self.optimize_routing(),
            "workflow_updates": self.refine_workflows(),
            "context_cleanup": self.cleanup_context(),
            "profit_snapshot": self.update_profit_snapshot(),
            "autonomy_adjustment": self.adjust_autonomy()
        }

        # Save nightly reflection
        with open(self.reflection_path, "r") as f:
            data = json.load(f)

        data["history"].append(summary)

        with open(self.reflection_path, "w") as f:
            json.dump(data, f, indent=4)

        return summary

    # ============================================================
    # 1. DAILY SUMMARY
    # ============================================================

    def generate_daily_summary(self):
        ledger = self.kernel.ledger.load()
        today = str(datetime.now()).split(" ")[0]

        today_entries = [e for e in ledger if today in e["timestamp"]]

        return {
            "total_events": len(today_entries),
            "engines_used": list({e["engine"] for e in today_entries}),
            "domains_touched": list({e["domain"] for e in today_entries})
        }

    # ============================================================
    # 2. FAILURE PATTERN DETECTION
    # ============================================================

    def detect_failure_patterns(self):
        failures = self.kernel.circuit.failures
        patterns = {}

        for engine, count in failures.items():
            if count >= 2:
                patterns[engine] = f"High failure rate: {count} failures"

        return patterns

    # ============================================================
    # 3. ROUTING OPTIMIZATION
    # ============================================================

    def optimize_routing(self):
        updates = []

        for domain, route in self.supervisor.routing_table.items():
            primary = route["primary"].__class__.__name__
            fallback = route["fallback"].__class__.__name__

            # If primary engine is failing too often → swap
            if self.kernel.circuit.failures.get(primary, 0) >= 3:
                route["primary"], route["fallback"] = route["fallback"], route["primary"]
                updates.append(f"Swapped primary/fallback for domain '{domain}'")

        return updates

    # ============================================================
    # 4. WORKFLOW REFINEMENT
    # ============================================================

    def refine_workflows(self):
        updates = []

        for chain_name, steps in self.workflow_executor.chains.items():
            if len(steps) > 5:
                updates.append(f"Workflow '{chain_name}' is long — consider optimization")

        return updates

    # ============================================================
    # 5. CONTEXT CLEANUP
    # ============================================================

    def cleanup_context(self):
        context_dir = "/home/keshanth/ARKA/ardhanarishvara/context/"
        cleaned = []

        for file in os.listdir(context_dir):
            path = os.path.join(context_dir, file)

            with open(path, "r") as f:
                data = json.load(f)

            if len(json.dumps(data)) > 50000:
                summarized = self.kernel.context.summarize(data)
                with open(path, "w") as f:
                    json.dump(summarized, f, indent=4)
                cleaned.append(file)

        return cleaned

    # ============================================================
    # 6. PROFIT SNAPSHOT UPDATE
    # ============================================================

    def update_profit_snapshot(self):
        return self.profit_engine.aggregate()

    # ============================================================
    # 7. AUTONOMY ADJUSTMENT
    # ============================================================

    def adjust_autonomy(self):
        failures = sum(self.kernel.circuit.failures.values())

        if failures == 0:
            return self.autonomy.escalate_to_full()

        if failures >= 5:
            return self.autonomy.reduce_to_partial()

        if failures >= 10:
            return self.autonomy.revoke_autonomy()

        return {"status": "no change"}
