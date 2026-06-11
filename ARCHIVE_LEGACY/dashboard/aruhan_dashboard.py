import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from ardhanarishvara.aruhan.aruhan_orchestrator import ARUHAN
from ardhanarishvara.execution.observer import observer


# =========================================================
# ARUHAN Dashboard
# =========================================================

class ARUHANDashboard:
    """
    Real-time dashboard for Ardhanarishvara OS.

    Features:
    - Live observer event stream
    - System status panel
    - Command execution panel
    - Autonomous mode controls
    """

    def __init__(self, embedder_model):
        self.aruhan = ARUHAN(embedder_model)
        self.app = FastAPI(title="ARUHAN Dashboard")

        # Connected WebSocket clients
        self.clients = set()

        # Register routes
        self._register_routes()

        # Subscribe to observer events
        observer.on("*", self._broadcast_event)

    # -----------------------------------------------------
    # Broadcast Observer Events to WebSocket Clients
    # -----------------------------------------------------
    async def _broadcast_event(self, event):
        data = {
            "type": "observer_event",
            "event_type": event.event_type,
            "payload": event.payload
        }
        message = json.dumps(data)

        dead = []
        for ws in self.clients:
            try:
                await ws.send_text(message)
            except:
                dead.append(ws)

        for ws in dead:
            self.clients.remove(ws)

    # -----------------------------------------------------
    # Register Routes
    # -----------------------------------------------------
    def _register_routes(self):

        @self.app.get("/")
        def dashboard_page():
            return HTMLResponse(self._html())

        @self.app.websocket("/ws")
        async def websocket_endpoint(ws: WebSocket):
            await ws.accept()
            self.clients.add(ws)

            # Send initial status
            await ws.send_text(json.dumps({
                "type": "status",
                "data": self.aruhan.status()
            }))

            try:
                while True:
                    msg = await ws.receive_text()
                    await self._handle_ws_message(ws, msg)
            except:
                self.clients.remove(ws)

    # -----------------------------------------------------
    # Handle WebSocket Messages
    # -----------------------------------------------------
    async def _handle_ws_message(self, ws, msg):
        try:
            data = json.loads(msg)
        except:
            return

        if data["type"] == "command":
            result = self.aruhan.execute(data["command"])
            await ws.send_text(json.dumps({
                "type": "command_result",
                "result": result
            }))

        if data["type"] == "autonomy_start":
            self.aruhan.start()

        if data["type"] == "autonomy_stop":
            self.aruhan.stop()

    # -----------------------------------------------------
    # Dashboard HTML
    # -----------------------------------------------------
    def _html(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <title>ARUHAN Dashboard</title>
    <style>
        body { font-family: Arial; background: #111; color: #eee; padding: 20px; }
        h1 { color: #4af; }
        .panel { background: #222; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
        .events { height: 300px; overflow-y: scroll; background: #000; padding: 10px; }
        input { width: 80%; padding: 8px; }
        button { padding: 8px 12px; margin-left: 10px; }
    </style>
</head>
<body>

<h1>ARUHAN MASTER ORCHESTRATOR — DASHBOARD</h1>

<div class="panel">
    <h2>System Status</h2>
    <pre id="status"></pre>
</div>

<div class="panel">
    <h2>Send Command to ARKA</h2>
    <input id="cmd" placeholder="Enter command...">
    <button onclick="sendCommand()">Send</button>
    <pre id="cmd_result"></pre>
</div>

<div class="panel">
    <h2>Autonomous Mode</h2>
    <button onclick="startAutonomy()">Start</button>
    <button onclick="stopAutonomy()">Stop</button>
</div>

<div class="panel">
    <h2>Observer Events</h2>
    <div class="events" id="events"></div>
</div>

<script>
    const ws = new WebSocket("ws://" + location.host + "/ws");

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "status") {
            document.getElementById("status").innerText =
                JSON.stringify(data.data, null, 2);
        }

        if (data.type === "command_result") {
            document.getElementById("cmd_result").innerText =
                JSON.stringify(data.result, null, 2);
        }

        if (data.type === "observer_event") {
            const box = document.getElementById("events");
            box.innerHTML += `<div>[${data.event_type}] ${JSON.stringify(data.payload)}</div>`;
            box.scrollTop = box.scrollHeight;
        }
    };

    function sendCommand() {
        const cmd = document.getElementById("cmd").value;
        ws.send(JSON.stringify({ type: "command", command: cmd }));
    }

    function startAutonomy() {
        ws.send(JSON.stringify({ type: "autonomy_start" }));
    }

    function stopAutonomy() {
        ws.send(JSON.stringify({ type: "autonomy_stop" }));
    }
</script>

</body>
</html>
        """

    # -----------------------------------------------------
    # FastAPI App Getter
    # -----------------------------------------------------
    def get_app(self):
        return self.app
