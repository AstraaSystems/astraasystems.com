from typing import Dict, Any
from app.core.mathematics_engine.state_space.kalman_filter import FinancialKalmanFilter

_MODULE_REGISTRY: Dict[str, Any] = {
    "state_space.kalman": FinancialKalmanFilter()
}

def compute(module: str, inputs: dict) -> Dict[str, Any]:
    if module not in _MODULE_REGISTRY:
        raise ValueError(f"Mathematical Sovereign module '{module}' is not registered.")
    return _MODULE_REGISTRY[module].run(inputs)
