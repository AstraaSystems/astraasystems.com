# ardhanarishvara/routing/task_router.py

class Router:
    def __init__(self):
        self.agents = {}

    def register_agent(self, name, handler):
        self.agents[name] = handler

    def route(self, agent, payload):
        return self.agents[agent](payload)

router = Router()
