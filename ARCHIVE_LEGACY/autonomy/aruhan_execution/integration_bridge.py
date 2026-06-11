from ardhanarishvara.routing.agents.astra_agent import AstraAgent
from ardhanarishvara.routing.agents.arka_agent import ArkaAgent

class AruhanIntegrationBridge:
    def __init__(self):
        self.astra = AstraAgent()
        self.arka = ArkaAgent()

    def route(self, task):
        if task.type == "reasoning":
            return self.astra.execute(task)
        return self.arka.execute(task)
