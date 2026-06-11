def decompose(goal: str):
    """
    Permanent semantic goal decomposition.
    Simple, general-purpose, domain-agnostic.
    """
    goal = goal.lower().strip()

    verbs = ["prepare", "deploy", "analyze", "configure", "install", "validate"]
    nouns = ["system", "environment", "deployment", "configuration", "package"]

    tasks = []

    for v in verbs:
        if v in goal:
            for n in nouns:
                if n in goal:
                    tasks.append(f"{v} {n}")

    if not tasks:
        tasks = [
            "understand goal",
            "identify requirements",
            "generate plan",
            "execute plan",
            "verify results"
        ]

    return {"goal": goal, "tasks": tasks}
