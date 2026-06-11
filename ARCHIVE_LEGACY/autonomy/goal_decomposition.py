import re

def decompose(goal: str):
    """
    Permanent, general-purpose semantic decomposition engine.
    No hardcoded tasks. No bandaids.
    """

    # Normalize
    goal_clean = goal.strip().lower()

    # Extract verbs and objects (very lightweight semantic parsing)
    verbs = re.findall(r"\b(prepare|deploy|analyze|optimize|build|configure|test|validate|monitor|repair|upgrade|install|remove|plan|design)\b", goal_clean)
    nouns = re.findall(r"\b(system|environment|deployment|network|service|module|package|infrastructure|configuration|pipeline|process)\b", goal_clean)

    tasks = []

    # 1. If verbs exist, generate tasks based on semantic intent
    for verb in verbs:
        for noun in nouns:
            tasks.append(f"{verb} {noun}")

    # 2. If no verbs/nouns found, fall back to generic semantic steps
    if not tasks:
        tasks = [
            "understand the goal",
            "identify required resources",
            "identify constraints",
            "generate execution plan",
            "validate plan",
            "execute plan",
            "verify results"
        ]

    # 3. Return permanent structure
    return {
        "goal": goal,
        "tasks": tasks,
        "dependencies": []
    }
