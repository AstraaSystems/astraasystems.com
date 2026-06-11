import json
from pathlib import Path

class QTuningPolicy:
    def __init__(self, config_filename="tuning_config.json"):
        config_path = Path(config_filename).resolve()
        
        # Safe Baseline Defaults
        self.min_multiplier = 0.70
        self.max_multiplier = 2.50
        self.instability_penalty = 0.80
        self.high_error_bonus = 0.40

        # Dynamic parameter consumption hook
        if config_path.exists():
            try:
                with config_path.open("r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.min_multiplier = cfg.get("min_multiplier", self.min_multiplier)
                    self.max_multiplier = cfg.get("max_multiplier", self.max_multiplier)
                    self.instability_penalty = cfg.get("instability_penalty", self.instability_penalty)
                    self.high_error_bonus = cfg.get("high_error_bonus", self.high_error_bonus)
                # Unobtrusive debugging line removed to keep the terminal execution ultra-clean
            except Exception:
                pass 

    def compute_multiplier(self, fusion, reflection_flag, temporal_trend):
        multiplier = 1.0
        multiplier += self.instability_penalty * fusion.instability
        disagreement = 1.0 - fusion.agreement
        multiplier += 0.5 * disagreement

        if reflection_flag == "HIGH_ERROR":
            multiplier += self.high_error_bonus
        elif reflection_flag == "MEDIUM_ERROR":
            multiplier += (self.high_error_bonus / 2.0)

        if temporal_trend == "DECLINING":
            multiplier += 0.2
        elif temporal_trend == "IMPROVING":
            multiplier -= 0.1

        if fusion.confidence > 0.8 and fusion.agreement > 0.8 and fusion.instability < 0.2:
            multiplier -= 0.15

        return max(self.min_multiplier, min(multiplier, self.max_multiplier))
