# aruhan/os/predictive/fusion_fingerprint.py

class FusionFingerprint:
    """
    Transforms volatile, real-time fusion telemetry into a discrete,
    hashable state identity signature for rapid memory lookup.
    """
    def create(self, fusion):
        return {
            "score": round(fusion.score, 2),
            "instability": round(fusion.instability, 2),
            "agreement": round(fusion.agreement, 2),
            "direction": fusion.direction.strip()
        }

    def key(self, fp):
        return f"{fp['score']}_{fp['instability']}_{fp['agreement']}_{fp['direction']}"
