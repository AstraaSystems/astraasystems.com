from ARKA.arka_core import ArkaCore

class ArkaRecursivePlanner:
    def __init__(self, ai=None, max_depth=5):
        self.core = ArkaCore(ai)
        self.max_depth = max_depth

    def recursive_plan(self, goal: str, depth=0):
        """
        Permanent recursive planning engine.
        ARKA will:
        - decompose the goal
        - evaluate each step
        - execute or refine
        - re-plan if needed
        - stop only when complete or max depth reached
        """

        if depth > self.max_depth:
            return {
                "goal": goal,
                "status": "max_depth_reached",
                "completed": [],
                "remaining": []
            }

        # Step 1: Decompose goal
        plan = self.core.adapter.apply_goal_decomposition(goal)
        steps = plan.get("tasks", [])

        completed = []
        remaining = []

        for step in steps:
            # Step 2: Evaluate before acting
            evaluation = self.core.adapter.apply_evaluation({"step": step})

            # Step 3: Policy validation
            self.core.adapter.apply_policy("arka_policy", {"step": step})

            # Step 4: Execute step (placeholder)
            result = {"step": step, "status": "done"}

            # Step 5: Log + telemetry
            self.core.adapter.apply_logging("arka_recursive_step", result)
            self.core.adapter.apply_telemetry("arka_recursive_step_completed", 1)

            # Step 6: Memory update
            self.core.remember(f"recursive_step_{step}", result)

            # Step 7: If execution failed → re-plan
            if result["status"] != "done":
                remaining.append(step)
                continue

            completed.append(step)

        # Step 8: If remaining tasks exist → recursive re-plan
        if remaining:
            return self.recursive_plan(" ".join(remaining), depth + 1)

        # Step 9: Final health check
        health = self.core.health_check()

        return {
            "goal": goal,
            "status": "complete",
            "completed": completed,
            "remaining": [],
            "health": health
        }
