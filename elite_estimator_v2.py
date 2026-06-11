import time
import numpy as np
import json
import os

LEDGER = "aruhan_ledger.jsonl"


class EliteEstimator:

    def __init__(self):
        self.last = None
        self.learn_score = 0.0
        self.weights = np.array([0.3, 0.25, 0.2])

    # -------------------------
    # CORE
    # -------------------------
    def normalize(self, x):
        return np.tanh(x)

    def vector(self, d):
        return np.array([
            self.normalize(d["material_cost_index"]),
            self.normalize(d["labor_cost_index"]),
            self.normalize(d["complexity"])
        ])

    def base_calc(self, d, v):
        return d["square_footage"] * 200 * (1 + np.dot(v, self.weights))

    def monte(self, d, runs=6):
        vals = []
        for _ in range(runs):
            n = d.copy()
            n["material_cost_index"] *= np.random.normal(1, 0.02)
            n["labor_cost_index"] *= np.random.normal(1, 0.02)
            v = self.vector(n)
            vals.append(self.base_calc(n, v))
        arr = np.array(vals)
        return arr.mean(), arr.std()

    # -------------------------
    # ENVIRONMENT
    # -------------------------
    def apply_env(self, base, d):
        env = d.get("environment", {})
        w = env.get("weather_severity", 0.2)
        s = env.get("season", 0.5)
        return base * (1 + w * 0.1) * (1 + s * 0.05)

    def risk(self, d):
        rf = d.get("risk_factors", {})
        base = sum(rf.values()) / len(rf) if rf else 0.2
        w = d.get("environment", {}).get("weather_severity", 0.2)
        return min(1, base + 0.3 * w)

    # -------------------------
    # SIMILARITY
    # -------------------------
    def similarity(self, a, b):
        keys = ["square_footage", "material_cost_index", "labor_cost_index"]
        s = 0
        c = 0
        for k in keys:
            if k in a and k in b:
                diff = abs(a[k] - b[k]) / (abs(a[k]) + 1e-6)
                s += (1 - diff)
                c += 1
        return s / c if c else 0

    def find_similar(self, d):
        if not os.path.exists(LEDGER):
            return []

        res = []
        with open(LEDGER, "r") as f:
            for line in f.readlines()[-30:]:
                e = json.loads(line)
                pi = e.get("input")
                pp = e.get("prediction")
                if pi and pp:
                    score = self.similarity(d, pi)
                    res.append((score, pp["base_estimate"]))

        res.sort(reverse=True)
        return res[:3]

    # -------------------------
    # ARCHETYPE
    # -------------------------
    def archetype(self, d):
        sqft = d["square_footage"]
        comp = d["complexity"]
        w = d.get("environment", {}).get("weather_severity", 0.2)

        size = "S" if sqft < 8000 else "M" if sqft < 20000 else "L"
        c = "H" if comp > 0.8 else "M" if comp > 0.5 else "L"
        env = "H" if w > 0.5 else "N"

        return f"{size}_{c}_{env}"

    def archetype_memory(self, arch):
        if not os.path.exists(LEDGER):
            return []

        vals = []
        with open(LEDGER, "r") as f:
            for line in f:
                e = json.loads(line)
                if e.get("arch") == arch:
                    vals.append(e["prediction"]["base_estimate"])
        return vals

    # -------------------------
    # LEARNING
    # -------------------------
    def learn(self, pred, actual):
        err = actual - pred
        r = err / (pred + 1e-6)

        score = max(0, 1 - abs(r))
        self.learn_score = 0.9 * self.learn_score + 0.1 * score

        self.weights *= (1 + np.clip(r, -0.01, 0.01))

    # -------------------------
    # LOG
    # -------------------------
    def log(self, inp, result, arch):

        entry = {
            "input": inp,
            "prediction": result,
            "arch": arch,
            "time": time.time()
        }

        with open(LEDGER, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # -------------------------
    # MAIN PREDICT (CRITICAL)
    # -------------------------
    def predict(self, d):

        t0 = time.time()

        v = self.vector(d)
        mean, vol = self.monte(d)

        base = mean if self.last is None else 0.3 * mean + 0.7 * self.last
        self.last = base

        base = self.apply_env(base, d)

        # similarity
        sims = self.find_similar(d)
        if sims:
            total = sum(s * val for s, val in sims)
            ws = sum(s for s, _ in sims)
            if ws > 0:
                base = 0.7 * base + 0.3 * (total / ws)

        # archetype
        arch = self.archetype(d)
        mem = self.archetype_memory(arch)
        if mem:
            base = 0.7 * base + 0.3 * (sum(mem) / len(mem))

        # auto-learning
        simulated_actual = base * np.random.normal(1.02, 0.015)
        self.learn(base, simulated_actual)

        risk = self.risk(d)
        signal = np.linalg.norm(v)

        raw_conf = (
            (1 - risk) * 0.4 +
            np.exp(-vol / 1e6) * 0.3 +
            min(1, signal) * 0.1 +
            self.learn_score * 0.15
        )

        confidence = np.clip(0.6 + raw_conf * 0.5, 0, 0.98)

        # OUTPUT LAYER
        low = base - 1.5 * vol
        high = base + 1.5 * vol

        breakdown = {
            "foundation": base * 0.15,
            "framing": base * 0.20,
            "electrical": base * 0.12,
            "plumbing": base * 0.10,
            "finishes": base * 0.18,
            "mechanical": base * 0.10,
            "overhead": base * 0.15
        }

        scenarios = [
            {"name": "material_spike", "impact": base * 0.08},
            {"name": "labor_shortage", "impact": base * 0.05},
            {"name": "delay_risk", "impact": base * 0.06},
            {"name": "optimized_plan", "impact": -base * 0.07}
        ]

        recommended = min(scenarios, key=lambda x: base + x["impact"])["name"]

        result = {
            "project_type": d.get("project_type", "unknown"),
            "base_estimate": float(base),
            "range": {"low": float(low), "high": float(high)},
            "confidence": float(confidence),
            "risk": float(risk),
            "archetype": arch,
            "recommended_plan": recommended,
            "scenarios": scenarios,
            "breakdown": breakdown,
            "health": {
                "volatility": float(vol),
                "latency_ms": (time.time() - t0) * 1000
            }
        }

        self.log(d, result, arch)

        return result


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":

    est = EliteEstimator()

    sample = {
        "project_type": "commercial",
        "square_footage": 12000,
        "material_cost_index": 1.1,
        "labor_cost_index": 1.05,
        "complexity": 0.8,
        "environment": {"weather_severity": 0.3, "season": 0.6},
        "risk_factors": {"weather": 0.2, "supply_chain": 0.3}
    }

    print(json.dumps(est.predict(sample), indent=2))
