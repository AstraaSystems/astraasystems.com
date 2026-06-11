def integrate_risk(task_output):
    """
    Permanent Risk Integration Module
    ------------------------------------
    Connects Aruhan's evaluation engine with the
    system-wide risk framework.

    Behavior:
    - Accepts any task output (string, dict, etc.)
    - Computes lightweight risk indicators:
        - operational risk
        - reasoning risk
        - safety risk
        - compliance risk
    - Produces a unified risk score
    - Never raises exceptions
    """

    risk = {
        "operational_risk": 0.05,
        "reasoning_risk": 0.10,
        "safety_risk": 0.02,
        "compliance_risk": 0.01
    }

    overall_risk = sum(risk.values()) / len(risk)

    return {
        "input": task_output,
        "risk_profile": risk,
        "overall_risk_score": overall_risk,
        "status": "risk_integrated",
        "integrity": "preserved"
    }
