# ardhanarishvara/astra/astra_core.py

from ardhanarishvara.astra.astra_adapter import AstraAdapter

class AstraCore:

    def __init__(self):
        self.adapter = AstraAdapter()

    def execute_goal(self, goal):
        try:
            decomposed = self.adapter.decompose_goal(goal)
            evaluated = self.adapter.evaluate_goal(decomposed)

            self.adapter.log_event(f"Executing goal: {goal}")
            self.adapter.record_metric("goal_execution", {"goal": goal})

            return {
                "success": True,
                "reason": "Goal executed",
                "result": evaluated
            }

        except Exception as e:
            return self.adapter.handle_error(e).__dict__
