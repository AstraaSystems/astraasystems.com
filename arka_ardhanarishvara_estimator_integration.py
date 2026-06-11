# Inside ArdhanarishvaraOS
def execute_strategy(self, signals, market_conditions):
    # 1. Estimate Cost
    cost_data = self.registry.get("estimator").predict(signals, "commercial_ground_up")
    
    # 2. Formulate Strategy
    strategist = self.registry.get("strategist")
    decision = strategist.evaluate(cost_data, market_conditions)
    
    # 3. Governance Check
    if cost_data["confidence"] < 0.6:
        return {"status": "HALT", "reason": "Low Confidence"}
        
    return {"cost": cost_data, "bid": decision}
def build_system() -> Tuple[Arka, ArdhanarishvaraOS, EliteEstimator]:
    # Use your high-fidelity construction schema
    construction_signals = [
        "labour_hours", "material_cost_index", "equipment_cost",
        "site_complexity", "schedule_pressure", "region_factor",
        "historical_variance", "bid_competitiveness"
    ]
    
    estimator = EliteEstimator(signal_names=construction_signals)
    os_kernel = ArdhanarishvaraOS()
    os_kernel.register_agent("estimator", estimator, role="predictive_compute", authority="bounded")
    arka = Arka(os_kernel)
    return arka, os_kernel, estimator
