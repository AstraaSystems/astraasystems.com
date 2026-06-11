from ardhanarishvara.autonomy.aruhan_self.self_correction_engine import SelfCorrectionEngine
from ardhanarishvara.autonomy.aruhan_self.self_reflection_engine import SelfReflectionEngine
from ardhanarishvara.autonomy.aruhan_self.self_reinforcement_engine import SelfReinforcementEngine
from ardhanarishvara.autonomy.aruhan_learning.adaptive_learning_engine import AdaptiveLearningEngine

class EngineAutonomyController:
    """
    Provides self-correction, self-reflection, reinforcement, and adaptive learning
    to all ASTRAA engines.
    """

    def __init__(self):
        self.corrector = SelfCorrectionEngine()
        self.reflector = SelfReflectionEngine()
        self.reinforcer = SelfReinforcementEngine()
        self.learner = AdaptiveLearningEngine()

    def process(self, task, result):
        """
        Apply autonomy layers to engine output.
        """
        corrected = self.corrector.apply(result)
        reflected = self.reflector.apply(corrected)
        reinforced = self.reinforcer.apply(reflected)
        learned = self.learner.update(task, reinforced)
        return learned
