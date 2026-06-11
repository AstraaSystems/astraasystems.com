class PolicyKernel:
    """
    POLICY KERNEL
    Enforces allow/deny/approval/escalation.
    """

    def __init__(self, arka, human_callback=None):
        self.arka = arka
        self.human_callback = human_callback
        self.audit_log = []

    def log(self, entry):
        self.audit_log.append(entry)

    def evaluate(self, action, context):
        # ARKA decides first
        arka_decision = self.arka.evaluate_policy(action, context)

        if arka_decision in ["allow", "deny"]:
            self.log({"action": action, "decision": arka_decision})
            return arka_decision

        # If ARKA cannot decide → escalate to human
        if arka_decision == "escalate":
            if self.human_callback:
                human_decision = self.human_callback(action, context)
                self.log({"action": action, "decision": human_decision})
                return human_decision

        # Default safety
        self.log({"action": action, "decision": "deny"})
        return "deny"
