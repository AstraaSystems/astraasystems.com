import sys
import threading
from ardhanarishvara.aruhan.aruhan_orchestrator import ARUHAN
from ardhanarishvara.execution.observer import observer


# =========================================================
# ARKA Command Shell (CLI)
# =========================================================

class ARKAShell:
    """
    ARKA Command Shell — the interactive terminal interface
    for the entire Ardhanarishvara OS.

    Features:
    - interactive command loop
    - ARUHAN integration
    - ARKA command execution
    - system status inspection
    - observer event logging
    """

    def __init__(self, embedder_model):
        self.aruhan = ARUHAN(embedder_model)
        self.running = False

        # Observer event log
        self.event_log = []
        observer.on("aruhan_command_received", self._log_event)
        observer.on("arka_command_received", self._log_event)
        observer.on("task_completed", self._log_event)
        observer.on("sector_comm_completed", self._log_event)
        observer.on("sector_analysis_completed", self._log_event)
        observer.on("sector_planning_completed", self._log_event)
        observer.on("sector_knowledge_completed", self._log_event)
        observer.on("sector_action_completed", self._log_event)

    # -----------------------------------------------------
    # Observer Event Logger
    # -----------------------------------------------------
    def _log_event(self, event):
        self.event_log.append(event)

    # -----------------------------------------------------
    # Start Shell
    # -----------------------------------------------------
    def start(self):
        self.running = True
        self.aruhan.start()

        print("\n==============================================")
        print("      ARKA COMMAND SHELL — ARUHAN OS")
        print("==============================================")
        print("Type commands to interact with the system.")
        print("Type 'help' for available commands.")
        print("Type 'exit' to quit.\n")

        while self.running:
            try:
                command = input("ARKA> ").strip()

                if command == "":
                    continue

                if command.lower() == "exit":
                    self.running = False
                    break

                if command.lower() == "help":
                    self._print_help()
                    continue

                if command.lower() == "status":
                    self._print_status()
                    continue

                if command.lower() == "events":
                    self._print_events()
                    continue

                # Default: send to ARUHAN → ARKA → Sectors
                result = self.aruhan.execute(command)
                print(f"\n[RESULT] {result}\n")

            except KeyboardInterrupt:
                print("\nExiting ARKA Shell.")
                break

            except Exception as e:
                print(f"\n[ERROR] {e}\n")

        self.aruhan.stop()

    # -----------------------------------------------------
    # Help Menu
    # -----------------------------------------------------
    def _print_help(self):
        print("\nAvailable Commands:")
        print("  help      - Show this help menu")
        print("  status    - Show system status")
        print("  events    - Show recent observer events")
        print("  exit      - Quit the shell")
        print("\nAny other input is treated as a natural language command.\n")

    # -----------------------------------------------------
    # System Status
    # -----------------------------------------------------
    def _print_status(self):
        status = self.aruhan.status()
        print("\nSystem Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        print()

    # -----------------------------------------------------
    # Event Log
    # -----------------------------------------------------
    def _print_events(self):
        print("\nRecent Events:")
        for event in self.event_log[-20:]:
            print(f"  - {event.event_type}: {event.payload}")
        print()
