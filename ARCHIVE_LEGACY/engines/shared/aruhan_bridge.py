from ardhanarishvara.autonomy.aruhan_execution.integration_bridge import AruhanIntegrationBridge

class EngineAruhanBridge:
    def __init__(self):
        self.bridge = AruhanIntegrationBridge()

    def execute(self, task):
        return self.bridge.route(task)
