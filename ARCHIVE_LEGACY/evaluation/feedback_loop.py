def feedback_loop(task_output, evaluation_data=None):
    """
    Permanent Feedback Loop Module
    ------------------------------------
    Provides a deterministic feedback engine
    for Aruhan's evaluation system.

    Behavior:
    - Accepts:
        - task_output: the result produced by Astra
        - evaluation_data: combined metrics, quality,
          compliance, and risk information
    - Determines whether:
        - output is acceptable
        - retry is needed
        - refinement is required
    - Returns a structured feedback object
    - Never raises exceptions
    """

    # Default behavior: accept output unless evaluation says otherwise
    needs_retry = False
    needs_refinement = False

    if isinstance(evaluation_data, dict):
        score = evaluation_data.get("overall_score", 1.0)
        risk = evaluation_data.get("overall_risk_score", 0.0)
        compliant = evaluation_data.get("is_compliant", True)

        # Simple deterministic rules
        if score < 0.6:
            needs_retry = True
        if risk > 0.3:
            needs_refinement = True
        if not compliant:
            needs_retry = True

    return {
        "input": task_output,
        "evaluation": evaluation_data,
        "needs_retry": needs_retry,
        "needs_refinement": needs_refinement,
        "status": "feedback_generated",
        "integrity": "preserved"
    }
