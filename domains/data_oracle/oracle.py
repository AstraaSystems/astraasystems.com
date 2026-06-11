from app.core.mathematics_engine.core_interface import compute

def run_data_oracle_node(payload: dict) -> dict:
    raw_price = payload.get("price", 0.0)
    volatility = payload.get("volatility", 0.0)
    math_truth = compute(
        module="state_space.kalman",
        inputs={"measurement": raw_price, "yield_spread_volatility": volatility}
    )
    velocity = math_truth["velocity"]
    signal = "NEUTRAL"
    if velocity > 0.05: signal = "BULLISH_MOMENTUM"
    elif velocity < -0.05: signal = "BEARISH_MOMENTUM"
    return {"signal_output": signal, "state_estimation": math_truth}
