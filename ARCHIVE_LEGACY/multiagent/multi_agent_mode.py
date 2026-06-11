import threading
import time
import uuid

from ardhanarishvara.aruhan.aruhan_orchestrator import ARUHAN
from ardhanarishvara.execution.observer import observer


# =========================================================
# Utility: Generate Agent IDs
# =========================================================

def generate_agent_id():
    return str(uuid.uuid4())


# =========================================================
# Agent Class
# =========================================================

class Agent:
    """
    A single autonomous agent inside the multi-agent system.

    Capabilities:
    - independent ARUHAN instance
    - message handling
    - task execution
    - inter-agent communication
    """

    def __init__(self, name, embedder_model, message_bus):
        self.name = name
        self.id = generate_agent_id()
        self.aruhan = ARUHAN(embedder_model)
        self.message_bus = message_bus
        self.running = False
        self.thread = None

        # Subscribe to message bus
        self.message_bus.register_agent(self)

    # -----------------------------------------------------
    # Send Message to Another Agent
    # -----------------------------------------------------
    def send(self, target_agent, content):
        self.message_bus.send_message(self.id, target_agent, content)

    # -----------------------------------------------------
    # Receive Message
    # -----------------------------------------------------
    def receive(self, sender_id, content):
        observer.emit("agent_message_received", {
            "agent": self.name,
            "from": sender_id,
            "content": content
        })

        # Default behavior: treat message as ARKA command
        return self.aruhan.execute(content)

    # -----------------------------------------------------
    # Autonomous Loop
    # -----------------------------------------------------
    def _loop(self):
        self.aruhan.start()

        while self.running:
            time.sleep(5)

        self.aruhan.stop()

    # -----------------------------------------------------
    # Start Agent
    # -----------------------------------------------------
    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

        observer.emit("agent_started", {"agent": self.name})

    # -----------------------------------------------------
    # Stop Agent
    # -----------------------------------------------------
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

        observer.emit("agent_stopped", {"agent": self.name})


# =========================================================
# Message Bus
# =========================================================

class MessageBus:
    """
    Central communication hub for all agents.

    Features:
    - agent registry
    - message routing
    - broadcast support
    """

    def __init__(self):
        self.agents = {}
        self.lock = threading.Lock()

    # -----------------------------------------------------
    # Register Agent
    # -----------------------------------------------------
    def register_agent(self, agent):
        with self.lock:
            self.agents[agent.id] = agent
            observer.emit("agent_registered", {"agent": agent.name})

    # -----------------------------------------------------
    # Send Message
    # -----------------------------------------------------
    def send_message(self, sender_id, target_id, content):
        with self.lock:
            if target_id not in self.agents:
                observer.emit("agent_message_error", {
                    "error": "unknown_target",
                    "target": target_id
                })
                return

            target_agent = self.agents[target_id]

        observer.emit("agent_message_sent", {
            "from": sender_id,
            "to": target_id,
            "content": content
        })

        return target_agent.receive(sender_id, content)

    # -----------------------------------------------------
    # Broadcast Message
    # -----------------------------------------------------
    def broadcast(self, sender_id, content):
        with self.lock:
            for agent_id, agent in self.agents.items():
                if agent_id != sender_id:
                    agent.receive(sender_id, content)


# =========================================================
# Multi-Agent System
# =========================================================

class MultiAgentSystem:
    """
    Multi-Agent Mode for Ardhanarishvara OS.

    Features:
    - multiple autonomous agents
    - shared message bus
    - inter-agent communication
    - distributed task execution
    """

    def __init__(self, embedder_model):
        self.embedder_model = embedder_model
        self.message_bus = MessageBus()
        self.agents = {}

    # -----------------------------------------------------
    # Create Agent
    # -----------------------------------------------------
    def create_agent(self, name):
        agent = Agent(name, self.embedder_model, self.message_bus)
        self.agents[agent.id] = agent
        return agent

    # -----------------------------------------------------
    # Start All Agents
    # -----------------------------------------------------
    def start_all(self):
        for agent in self.agents.values():
            agent.start()

    # -----------------------------------------------------
    # Stop All Agents
    # -----------------------------------------------------
    def stop_all(self):
        for agent in self.agents.values():
            agent.stop()

    # -----------------------------------------------------
    # Send Message Between Agents
    # -----------------------------------------------------
    def send(self, sender_id, target_id, content):
        return self.message_bus.send_message(sender_id, target_id, content)

    # -----------------------------------------------------
    # Broadcast Message
    # -----------------------------------------------------
    def broadcast(self, sender_id, content):
        self.message_bus.broadcast(sender_id, content)
