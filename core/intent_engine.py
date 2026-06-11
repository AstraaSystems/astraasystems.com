import json, time, math

# === INTENT ENGINE V2 (AUTONOMY-READY) ===

INTENT_PATH = "/home/keshanth/ARKA/ardhanarishvara/core/system_intent.json"

def load_intent():
    with open(INTENT_PATH) as f:
        return json.load(f)

def score_violation(value, target, weight):
    """
    Returns a normalized violation score between 0 and 1.
    """
    if target == 0:
        return 0
    diff = max(0, value - target)
    return min(1, (diff / target) * weight)

def evaluate(agent, output):
    intent = load_intent()
    domain = intent.get(agent, {})
    weights = domain.get("weights", {})

    result = {
        "approved": True,
        "score": 1.0,
        "violations": [],
        "ts": time.time()
    }

    # SAFETY FIRST
    if output.get("action") in intent["safety"]["human_required"]:
        result["approved"] = False
        result["violations"].append("requires_human_approval")
        result["score"] = 0
        return result

    # FINANCE ENGINE
    if agent == "finance":
        margin = output.get("margin", 1)
        if margin < domain["min_margin"]:
            v = score_violation(domain["min_margin"] - margin, domain["min_margin"], weights["margin"])
            result["violations"].append("margin_below_min")
            result["score"] -= v

        if output.get("amount", 0) > domain["max_daily_spend"]:
            v = score_violation(output["amount"], domain["max_daily_spend"], weights["risk"])
            result["violations"].append("exceeds_daily_spend")
            result["score"] -= v

    # OPERATIONS ENGINE
    if agent == "operations":
        delay = output.get("delay_min", 0)
        if delay > domain["max_route_delay_min"]:
            v = score_violation(delay, domain["max_route_delay_min"], weights["delay"])
            result["violations"].append("route_delay_violation")
            result["score"] -= v

    # BUSINESS ENGINE
    if agent == "business":
        latency = output.get("latency", 0)
        if latency > domain["max_quote_latency_sec"]:
            v = score_violation(latency, domain["max_quote_latency_sec"], weights["latency"])
            result["violations"].append("latency_violation")
            result["score"] -= v

    # FINAL DECISION
    if result["score"] < intent["safety"]["max_risk_score"]:
        result["approved"] = False

    return result
