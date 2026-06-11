import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any
from datetime import datetime

# ==========================================
# 1. DATA MODELS & STORAGE LAYER
# ==========================================

@dataclass
class ReflectionRecord:
    task_id: str
    timestamp: str
    intent: str
    origin: str
    predictions: Dict[str, Any]
    actual_outcome: Dict[str, Any]
    deviation_score: float
    confidence_score: float
    reflection_summary: str
    recommended_adjustments: List[str] = field(default_factory=list)

@staticmethod
    def now():
        # Use explicit timezone-aware UTC to resolve the deprecation warning
        from datetime import timezone
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

class ReflectionStore:
    def __init__(self, path="reflection_ledger.jsonl"):
        self.path = Path(path)
        self.path.touch(exist_ok=True)

    def save(self, reflection_record: ReflectionRecord):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(reflection_record)) + "\n")

# ==========================================
# 2. ANALYSIS & ADAPTATION ROUTING
# ==========================================

class DeviationAnalyzer:
    def analyse(self, predictions: dict, actual_outcome: dict) -> dict:
        deviation_score = 0.0
        notes = []
        
        predicted_signal = predictions.get("dataoracle", {}).get("signal")
        actual_direction = actual_outcome.get("market_direction")
        
        if predicted_signal == "bearish_momentum" and actual_direction == "rebounded":
            deviation_score += 0.6
            notes.append("Momentum prediction diverged from realised market direction.")
            
        predicted_confidence = predictions.get("dataoracle", {}).get("confidence", 0.0)
        
        if predicted_confidence > 0.75 and deviation_score > 0.5:
            deviation_score += 0.2
            notes.append("Confidence was too high relative to realised accuracy.")
            
        deviation_score = min(deviation_score, 1.0)
        return {"deviation_score": deviation_score, "notes": notes}

class AdaptationRouter:
    def recommend(self, deviation_report: dict, predictions: dict, actual_outcome: dict) -> list:
        adjustments = []
        score = deviation_report["deviation_score"]
        notes = deviation_report["notes"]
        
        if score >= 0.5:
            adjustments.append("raise_kalman_process_noise_sensitivity")
            adjustments.append("lower_confidence_when_regime_is_unstable")
            
        # Extract safely from dictionary mapping
        volatility_regime = actual_outcome.get("volatility_regime", "")
        if "temporary volatility spike" in str(volatility_regime).lower():
            adjustments.append("add_short_horizon_regime_memory_weighting")
            
        if any("Confidence was too high" in note for note in notes):
            adjustments.append("tighten_confidence_calibration")
            
        return adjustments

class TemporalIndex:
    def trend_score(self, recent_reflections: list) -> float:
        if not recent_reflections:
            return 0.0
        avg = sum(r.get("deviation_score", 0.0) for r in recent_reflections) / len(recent_reflections)
        return avg

# ==========================================
# 3. CORE ORCHESTRATOR
# ==========================================

class ReflectionEngine:
    def __init__(self, store_path="reflection_ledger.jsonl"):
        self.store = ReflectionStore(store_path)
        self.deviation_analyzer = DeviationAnalyzer()
        self.adaptation_router = AdaptationRouter()
        self.temporal_index = TemporalIndex()

    def reflect(self, task_id: str, intent: str, origin: str, predictions: dict, actual_outcome: dict) -> ReflectionRecord:
        deviation_report = self.deviation_analyzer.analyse(predictions, actual_outcome)
        adjustments = self.adaptation_router.recommend(deviation_report, predictions, actual_outcome)
        summary = self._build_summary(deviation_report, adjustments)
        
        record = ReflectionRecord(
            task_id=task_id,
            timestamp=ReflectionRecord.now(),
            intent=intent,
            origin=origin,
            predictions=predictions,
            actual_outcome=actual_outcome,
            deviation_score=deviation_report["deviation_score"],
            confidence_score=predictions.get("dataoracle", {}).get("confidence", 0.0),
            reflection_summary=summary,
            recommended_adjustments=adjustments
        )
        
        self.store.save(record)
        return record

    def _build_summary(self, deviation_report: dict, adjustments: list) -> str:
        notes = deviation_report.get("notes", [])
        if not notes:
            return "System prediction aligned with observed outcome."
        base = " | ".join(notes)
        if adjustments:
            base += " | Recommended: " + ", ".join(adjustments)
        return base

# ==========================================
# 4. EXECUTION HARNESS
# ==========================================

if __name__ == "__main__":
    print("\n[ARKA GOVERNANCE]: Initializing Reflection Engine Prototype...")
    engine = ReflectionEngine()
    
    simulated_predictions = {
        "dataoracle": {"signal": "bearish_momentum", "confidence": 0.78},
        "lux": {"risk_posture": "defensive"}
    }
    
    simulated_reality = {
        "market_direction": "rebounded",
        "volatility_regime": "temporary volatility spike"
    }
    
    print("\n[SYSTEM]: Processing task execution and observing reality...")
    
    reflection_result = engine.reflect(
        task_id="task-arka-001",
        intent="analyse treasury volatility",
        origin="arka_governance_core",
        predictions=simulated_predictions,
        actual_outcome=simulated_reality
    )
    
    print("\n================ METACOGNITIVE REPORT ================")
    print(f"Task ID      : {reflection_result.task_id}")
    print(f"Deviation    : {reflection_result.deviation_score}")
    print(f"Summary      : {reflection_result.reflection_summary}")
    print(f"Adaptations  : {reflection_result.recommended_adjustments}")
    print("======================================================")
    print("\n[STORAGE]: Reflection safely written to local reflection_ledger.jsonl")
