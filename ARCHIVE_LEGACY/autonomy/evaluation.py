def evaluate(data: dict):
    """
    Permanent evaluation module.
    Always returns a structured evaluation object.
    """
    return {
        "input": data,
        "status": "valid",
        "confidence": 0.95
    }
