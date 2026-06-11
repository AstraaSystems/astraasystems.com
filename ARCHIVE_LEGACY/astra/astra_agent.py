from ardhanarishvara.astra.astra_adapter import AstraAdapter

class AstraAgent:
    """
    Permanent Astra Agent.
    Astra is ARKA's execution worker AI.
    Responsibilities:
    - Receive delegated tasks from ARKA
    - Execute tasks through AstraCore
    - Handle errors safely
    - Return structured results to ARKA
    """

    def __init__(self):
        self.core = AstraCore()

    def run(self, task: str):
        """
        Execute a task with full safety and motherboard compliance.
        """
        try:
            return self.core.execute_task(task)
        except Exception as e:
            return self.core.safe_recovery(e)
