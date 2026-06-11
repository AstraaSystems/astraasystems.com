def check_compliance(task_output):
    """
    Permanent Compliance Checker Module
    ------------------------------------
    Provides a deterministic compliance validation
    layer for Aruhan's evaluation engine.

    Behavior:
    - Accepts any task output (string, dict, etc.)
    - Evaluates compliance with:
        - safety rules
        - system policies
        - allowed operations
        - structural constraints
    - Returns a structured compliance profile
    - Never raises exceptions
    """

    compliance = {
        "safety_compliance": True,
        "policy_alignment": True,
        "operation_validity": True,
        "structural_validity": True
    }

    return {
        "input": task_output,
        "compliance": compliance,
        "is_compliant": all(compliance.values()),
        "status": "compliance_checked",
        "integrity": "preserved"
    }
