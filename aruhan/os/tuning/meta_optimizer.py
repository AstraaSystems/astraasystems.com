import json
import numpy as np
from pathlib import Path

class AruhanMetaOptimizer:
    def __init__(self, ledger_filename="aruhan_ledger.jsonl", config_filename="tuning_config.json"):
        self.ledger_path = Path(ledger_filename).resolve()
        self.config_path = Path(config_filename).resolve()

    def load_historical_data(self):
        if not self.ledger_path.exists():
            return []
        with self.ledger_path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def analyze_and_autotune(self):
        records = self.load_historical_data()
        if not records:
            return

        measurements = np.array([r["measurement"] for r in records])
        predictions = np.array([r["prediction"] for r in records])
        q_multipliers = np.array([r["q_multiplier"] for r in records])
        
        rmse = np.sqrt(np.mean((measurements - predictions) ** 2))
        max_error = np.max(np.abs(measurements - predictions))
        avg_q = np.mean(q_multipliers)

        print("\n📊 RUNTIME META-OPTIMIZER ANALYSIS")
        print(f"   ├─ Total Dataset Window  : {len(records)} steps")
        print(f"   ├─ Measured RMSE         : {rmse:.4f}")
        print(f"   └─ Peak Structural Shock : {max_error:.4f}")

        # Default Optimized Config Bounds
        config = {
            "min_multiplier": 0.70,
            "max_multiplier": 2.50,
            "instability_penalty": 0.80,
            "high_error_bonus": 0.40
        }

        # AUTONOMOUS OPTIMIZATION HEURISTIC ENGINE
        # If RMSE > 0.50 and the system isn't adapting fast enough, lift the tuning thresholds
        if rmse > 0.50 and avg_q < 1.8:
            print("\n⚙️ [AUTO-TUNING] System lag detected. Scaling up responsiveness policies...")
            config["min_multiplier"] = 0.90
            config["instability_penalty"] = 1.20
            config["high_error_bonus"] = 0.60
        else:
            print("\n⚙️ [AUTO-TUNING] Performance within nominal bounds. Maintaining optimal policy baseline.")

        # Save configuration to disk for the next loop run
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"   └─ Parameter policy state synchronized to: {self.config_path}")
