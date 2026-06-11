import time
import threading
import random

from ardhanarishvara.aruhan.aruhan_orchestrator import ARUHAN
from ardhanarishvara.execution.observer import observer


# =========================================================
# Autonomous Mode Engine
# =========================================================

class AutonomousMode:
    """
    Autonomous Mode for Ardhanarishvara OS.

    Capabilities:
    - self-generated goals
    - self-initiated tasks
    - periodic evaluation
    - adaptive behavior
    - ARUHAN-driven orchestration
    """

    def __init__(self, embedder_model):
        self.aruhan = ARUHAN(embedder_model)
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        # Internal state
        self.state = {
            "cycles": 0,
            "goals_completed": 0,
            "last_goal": None
        }

        # Goal templates
        self.goal_templates = [
            "analyze system performance",
            "summarize recent memory",
            "generate a plan for optimization",
            "retrieve key insights from memory",
            "execute a diagnostic routine",
            "improve internal reasoning strategy"
        ]

    # -----------------------------------------------------
    # Generate Autonomous Goal
    # -----------------------------------------------------
    def _generate_goal(self):
        goal = random.choice(self.goal_templates)
        with self.lock:
            self.state["last_goal"] = goal
        observer.emit("autonomy_goal_generated", {"goal": goal})
        return goal

    # -----------------------------------------------------
    # Execute Autonomous Goal
    # -----------------------------------------------------
    def _execute_goal(self, goal):
        observer.emit("autonomy_goal_started", {"goal": goal})
        result = self.aruhan.execute(goal)
        observer.emit("autonomy_goal_completed", {"goal": goal, "result": result})

        with self.lock:
            self.state["goals_completed"] += 1

    # -----------------------------------------------------
    # Autonomous Cycle
    # -----------------------------------------------------
    def _cycle(self):
        with self.lock:
            self.state["cycles"] += 1

        observer.emit("autonomy_cycle", {"cycle": self.state["cycles"]})

        # Step 1: Generate goal
        goal = self._generate_goal()

        # Step 2: Execute goal
        self._execute_goal(goal)

        # Step 3: Evaluate system state
        self._evaluate()

    # -----------------------------------------------------
    # Evaluation Logic
    # -----------------------------------------------------
    def _evaluate(self):
        """
        Simple evaluation logic.
        Future: reward models, reinforcement learning, adaptive planning.
        """
        score = random.uniform(0.5, 1.0)
        observer.emit("autonomy_evaluation", {"score": score})

    # -----------------------------------------------------
    # Background Loop
    # -----------------------------------------------------
    def _loop(self):
        self.aruhan.start()

        while self.running:
            try:
                self._cycle()
            except Exception as e:
                observer.emit("autonomy_error", {"error": str(e)})

            time.sleep(8)  # Autonomous cycle interval

        self.aruhan.stop()

    # -----------------------------------------------------
    # Start Autonomous Mode
    # -----------------------------------------------------
    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

        observer.emit("autonomy_started", {"timestamp": time.time()})

    # -----------------------------------------------------
    # Stop Autonomous Mode
    # -----------------------------------------------------
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

        observer.emit("autonomy_stopped", {"timestamp": time.time()})

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------
    def status(self):
        return {
            "cycles": self.state["cycles"],
            "goals_completed": self.state["goals_completed"],
            "last_goal": self.state["last_goal"]
        }
