from ardhanarishvara.arka.arka_core import ARKACommandCore
from ardhanarishvara.execution.routing_layer import (
    TaskRouter,
    EngineAdapter,
    SectorAdapter
)

from ardhanarishvara.engines.engines import (
    TaskEngine,
    ReasoningEngine,
    DomainEngine
)

from ardhanarishvara.sectors.astraa_sectors import (
    CommunicationSector,
    AnalysisSector,
    PlanningSector,
    KnowledgeSector,
    ActionSector
)


# =========================================================
# Full System Integration Layer
# =========================================================

class ArdhanarishvaraSystem:
    """
    The unified AI system that integrates:
    - ARKA Command Core
    - ASTRAA Sectors
    - Engines
    - Routing Layer
    - Memory System
    - Execution Kernel
    - Safety Hooks
    - Observer System
    """

    def __init__(self, embedder_model):
        # Core
        self.arka = ARKACommandCore(embedder_model)

        # Engines
        self.task_engine = TaskEngine("task_engine")
        self.reasoning_engine = ReasoningEngine("reasoning_engine")
        self.domain_engine = DomainEngine("domain_engine")

        # Sectors
        self.comm_sector = CommunicationSector("communication", embedder_model)
        self.analysis_sector = AnalysisSector("analysis", embedder_model)
        self.planning_sector = PlanningSector("planning", embedder_model)
        self.knowledge_sector = KnowledgeSector("knowledge", embedder_model)
        self.action_sector = ActionSector("action", embedder_model)

        # Routing Layer
        self._register_engines()
        self._register_sectors()

    # -----------------------------------------------------
    # Register Engines
    # -----------------------------------------------------
    def _register_engines(self):
        self.arka.register_engine("task_engine", EngineAdapter(self.task_engine))
        self.arka.register_engine("reasoning_engine", EngineAdapter(self.reasoning_engine))
        self.arka.register_engine("domain_engine", EngineAdapter(self.domain_engine))

    # -----------------------------------------------------
    # Register Sectors
    # -----------------------------------------------------
    def _register_sectors(self):
        self.arka.register_sector("communication", SectorAdapter(self.comm_sector))
        self.arka.register_sector("analysis", SectorAdapter(self.analysis_sector))
        self.arka.register_sector("planning", SectorAdapter(self.planning_sector))
        self.arka.register_sector("knowledge", SectorAdapter(self.knowledge_sector))
        self.arka.register_sector("action", SectorAdapter(self.action_sector))

    # -----------------------------------------------------
    # Execute Command
    # -----------------------------------------------------
    def execute(self, command: str):
        """
        High-level entry point for the entire AI system.
        """
        return self.arka.interpret(command)
