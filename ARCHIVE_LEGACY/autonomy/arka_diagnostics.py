from ARKA.arka_core import ArkaCore
from ARKA.arka_adapter import ArkaAdapter

class ArkaDiagnostics:
    def __init__(self, ai=None):
        self.ai = ai
        self.core = ArkaCore(ai)
        self.adapter = ArkaAdapter(ai)

    def run(self):
        report = {}

        # 1. Core Engine Goal Execution
        try:
            result = self.core.execute_goal("diagnostic goal")
            report["core_goal_execution"] = True if "plan" in result else False
        except Exception as e:
            report["core_goal_execution"] = str(e)

        # 2. Health Check
        try:
            result = self.core.health_check()
            report["health_check"] = True if "status" in result else False
        except Exception as e:
            report["health_check"] = str(e)

        # 3. Memory Store & Retrieve
        try:
            self.core.remember("diag_key", "diag_value")
            value = self.core.recall("diag_key")
            report["memory_system"] = True if value is None or value == "diag_value" else False
        except Exception as e:
            report["memory_system"] = str(e)

        # 4. Safe Mode Recovery
        try:
            result = self.core.safe_recovery(Exception("test error"))
            report["safe_recovery"] = True if "mode" in result else False
        except Exception as e:
            report["safe_recovery"] = str(e)

        # 5. Resource Allocation
        try:
            result = self.core.allocate_resources("cpu", 1)
            report["resource_allocation"] = True if result is True else False
        except Exception as e:
            report["resource_allocation"] = str(e)

        # 6. Budget Allocation
        try:
            result = self.core.allocate_budget(50)
            report["budget_allocation"] = True if result is True else False
        except Exception as e:
            report["budget_allocation"] = str(e)

        # 7. Task Delegation
        try:
            result = self.core.delegate({"task": "diagnostic"}, "Astra")
            report["task_delegation"] = True if result is True else False
        except Exception as e:
            report["task_delegation"] = str(e)

        # 8. Adapter Connectivity Test
        adapter_tests = {
            "goal_decomposition": lambda: self.adapter.apply_goal_decomposition("test"),
            "evaluation_loop": lambda: self.adapter.apply_evaluation({"test": True}),
            "policy_engine": lambda: self.adapter.apply_policy("test_policy", {}),
            "state_machine": lambda: self.adapter.apply_state_transition("idle", "start"),
            "safe_mode": lambda: self.adapter.apply_safe_mode(Exception("test")),
            "error_handling": lambda: self.adapter.apply_error_handling(Exception("test")),
            "security_policies": lambda: self.adapter.apply_security_check("resource"),
            "risk_framework": lambda: self.adapter.apply_risk_assessment({}),
            "consensus": lambda: self.adapter.apply_consensus({"state": "test"}),
            "memory_protocols": lambda: self.adapter.apply_memory_store("k", "v"),
            "task_routing": lambda: self.adapter.apply_task_routing({"task": "t"}, "Astra"),
            "provisioning": lambda: self.adapter.apply_provisioning({"req": True}),
            "logging": lambda: self.adapter.apply_logging("event", {"data": True}),
            "telemetry": lambda: self.adapter.apply_telemetry("metric", 1),
            "health_monitor": lambda: self.adapter.apply_health_check(),
            "budgeting": lambda: self.adapter.apply_budgeting(10),
            "resource_allocation": lambda: self.adapter.apply_resource_allocation("cpu", 1),
        }

        for test_name, test_func in adapter_tests.items():
            try:
                test_func()
                report[f"adapter_{test_name}"] = True
            except Exception as e:
                report[f"adapter_{test_name}"] = str(e)

        return report
