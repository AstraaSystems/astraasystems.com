from ardhanarishvara.engines.shared.aruhan_bridge import EngineAruhanBridge
from ardhanarishvara.engines.autonomy.engine_autonomy_controller import EngineAutonomyController

class BusinessAruhanAdapter:
    def __init__(self):
        self.aruhan = EngineAruhanBridge()
        self.autonomy = EngineAutonomyController()

    def run(self, task):
        task.type = "business"
        result = self.aruhan.execute(task)
        return self.autonomy.process(task, result)
