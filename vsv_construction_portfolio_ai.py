from enum import Enum

class StrategyMode(Enum):
    PRESERVATION = "PRESERVATION"
    BALANCED = "BALANCED"
    GROWTH = "GROWTH"
class ArdhanarishvaraOS:
    def __init__(self, estimator):
        self.estimator = estimator
        self.governance = GovernanceEngine()
        self.healer = SelfHealingEngine() # The new Autonomous Core
        
    def cycle(self, signals, scenario):
        # 1. Standard Operation
        result = self.estimator.predict(signals, scenario)
        decision = self.governance.route(result)
        
        # 2. Autonomous Healing Step
        snapshot = self.snapshot()
        issues = self.healer.evaluate(snapshot)
        if issues:
            corrections = self.healer.apply_corrections(self, issues)
            # Log these to your Arka audit tail
            print(f"[System Healing] {corrections}")
            
        return result

class Arka:
    def __init__(self, os_kernel, mode: StrategyMode = StrategyMode.BALANCED):
        self.os = os_kernel
        self.mode = mode

    def set_mode(self, mode: StrategyMode):
        self.mode = mode
        # Propagate to kernel if necessary

class GovernanceEngine:
    def route(self, evaluation, mode: StrategyMode):
        confidence = evaluation["estimator"]["confidence"]
        
        # Thresholds based on strategy
        thresholds = {
            StrategyMode.PRESERVATION: 0.90,
            StrategyMode.BALANCED: 0.75,
            StrategyMode.GROWTH: 0.60
        }
        
        target = thresholds.get(mode, 0.75)
        
        if confidence > target:
            return "EXECUTE_BID"
        elif confidence > (target - 0.2):
            return "REVIEW_AND_VALIDATE"
        return "ESCALATE_OR_DECLINE"
class SelfHealingEngine:
    def __init__(self, sensitivity: float = 0.05):
        self.sensitivity = sensitivity  # How much to correct (0.05 = 5% nudge)

    def evaluate(self, snapshot: Dict) -> List[str]:
        issues = []
        # Check 1: Accuracy Drift
        for scenario, metrics in snapshot["estimator"].items():
            if metrics.get("rmse", 0) > 0.18:
                issues.append(f"ACCURACY_DRIFT:{scenario}")
        
        # Check 2: Decision Paralysis
        if snapshot["audit_counts"].get("ESCALATE_OR_DECLINE", 0) > 10:
            issues.append("GOVERNANCE_PARALYSIS")
            
        return issues

    def apply_corrections(self, os_kernel, issues: List[str]):
        corrections = []
        
        for issue in issues:
            if "ACCURACY_DRIFT" in issue:
                # Nudge estimator weights to flatten and reduce overfitting
                os_kernel.estimator.adjust_weights(decay=0.98)
                corrections.append("Flattened estimator weights to reduce drift.")
                
            elif "GOVERNANCE_PARALYSIS" in issue:
                # Lower threshold to encourage throughput
                os_kernel.governance.threshold -= self.sensitivity
                corrections.append("Lowered governance threshold to exit paralysis.")
        
        return corrections
class DebugEngine:
    def __init__(self):
        self.log = deque(maxlen=100)

    def analyze(self, result: Dict, signals: Dict, scenario: Dict) -> Dict:
        # 1. Signal Health
        signal_issues = [f"{k}: NULL" for k, v in signals.items() if v is None]
        
        # 2. Context Health
        required = ["sector", "project_type", "complexity_class"]
        missing_context = [k for k in required if k not in scenario]
        
        # 3. Estimator Health
        est = result["estimator"]
        est_status = "OK" if est.get("confidence", 0) > 0.3 else "LOW_CONFIDENCE"
        
        # 4. Decision Alignment
        route = result.get("route", {}).get("route", "UNKNOWN")
        rec = result.get("bid_decision", {}).get("recommendation", "UNKNOWN")
        decision_status = "CONFLICT" if (route == "ESCALATE_OR_DECLINE" and rec != "NO_BID") else "OK"
        
        # 5. Execution Flags
        trade_risk = result.get("subtrade_analysis", {}).get("total_trade_risk", 0)
        prod = result.get("crew_productivity", {}).get("productivity_index", 1.0)
        exec_flags = []
        if trade_risk > 0.75: exec_flags.append("TRADE_RISK_HIGH")
        if prod < 0.65: exec_flags.append("LOW_PRODUCTIVITY")

        report = {
            "signal_issues": signal_issues,
            "scenario_valid": len(missing_context) == 0,
            "estimator_status": est_status,
            "decision_status": decision_status,
            "execution_flags": exec_flags,
            "timestamp": time.time()
        }
        
        self.log.append(report)
        return report

