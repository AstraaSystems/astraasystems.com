class GovernanceGateway:
    """
    GOVERNANCE GATEWAY
    Runtime enforcement between Aruhan, ARKA, ASTRA, and tools.
    """

    def __init__(self, policy_kernel):
        self.policy = policy_kernel

    def request_action(self, action, context):
        decision = self.policy.evaluate(action, context)

        if decision == "allow":
            return {"status": "allowed", "action": action}

        if decision == "deny":
            return {"status": "denied", "reason": "Policy Kernel"}

        if decision == "escalate":
            return {"status": "pending_human"}

        return {"status": "unknown"}
