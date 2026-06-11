from fastapi import FastAPI
from pydantic import BaseModel

from ardhanarishvara.aruhan.aruhan_orchestrator import ARUHAN


# =========================================================
# Request Models
# =========================================================

class CommandRequest(BaseModel):
    command: str


# =========================================================
# API Layer
# =========================================================

class ArdhanarishvaraAPI:
    """
    REST API layer for Ardhanarishvara OS.

    Exposes:
    - /execute     → ARKA command execution
    - /status      → ARUHAN system status
    - /autonomy/start
    - /autonomy/stop
    """

    def __init__(self, embedder_model):
        self.aruhan = ARUHAN(embedder_model)
        self.app = FastAPI(title="Ardhanarishvara OS API")

        # Register routes
        self._register_routes()

    # -----------------------------------------------------
    # Route Registration
    # -----------------------------------------------------
    def _register_routes(self):

        @self.app.post("/execute")
        def execute_command(req: CommandRequest):
            result = self.aruhan.execute(req.command)
            return {"result": result}

        @self.app.get("/status")
        def system_status():
            return self.aruhan.status()

        @self.app.post("/autonomy/start")
        def start_autonomy():
            self.aruhan.start()
            return {"status": "autonomy_started"}

        @self.app.post("/autonomy/stop")
        def stop_autonomy():
            self.aruhan.stop()
            return {"status": "autonomy_stopped"}

    # -----------------------------------------------------
    # FastAPI Application Getter
    # -----------------------------------------------------
    def get_app(self):
        return self.app
