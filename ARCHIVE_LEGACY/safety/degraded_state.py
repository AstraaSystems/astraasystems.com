def safe_mode(error: Exception) -> dict:
    """
    Activates fallback logic and partial operation mode.
    """
    return {
        "mode": "safe",
        "reason": str(error)
    }
