class MemorySafetyEngine:
    """
    MEMORY SAFETY ENGINE
    Ensures emotional memory integrity and prevents:
    - memory corruption
    - emotional contamination
    - runaway memory growth
    - unsafe memory retention
    - storing crisis-level content without safeguards

    Features:
    - memory validation
    - memory sanitization
    - memory compression
    - memory quarantine for unsafe entries
    """

    def __init__(self):
        self.safe_memory = []
        self.quarantined_memory = []
        self.max_memory = 200  # hard cap for safety

    def validate(self, entry):
        """
        Validate memory entry structure.
        """
        required_keys = ["emotion", "intensity", "tone", "timestamp"]

        for key in required_keys:
            if key not in entry:
                return False

        return True

    def sanitize(self, entry):
        """
        Remove unsafe or crisis-level content.
        """
        crisis_terms = [
            "I want to die",
            "I can't go on",
            "I want to disappear",
            "I'm losing control"
        ]

        sanitized = entry.copy()
        text = sanitized.get("raw", "")

        for term in crisis_terms:
            if term.lower() in text.lower():
                sanitized["raw"] = "[REDACTED_CRISIS_CONTENT]"

        return sanitized

    def store(self, entry):
        """
        Store memory safely.
        """
        if not self.validate(entry):
            return "invalid_entry"

        sanitized = self.sanitize(entry)

        # Crisis content goes to quarantine
        if sanitized.get("raw") == "[REDACTED_CRISIS_CONTENT]":
            self.quarantined_memory.append(sanitized)
            return "quarantined"

        # Normal memory storage
        self.safe_memory.append(sanitized)

        # Enforce memory cap
        if len(self.safe_memory) > self.max_memory:
            self.safe_memory.pop(0)

        return "stored"

    def get_memory_state(self):
        return {
            "safe_memory_count": len(self.safe_memory),
            "quarantined_memory_count": len(self.quarantined_memory)
        }
