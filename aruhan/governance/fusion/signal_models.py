from dataclasses import dataclass

@dataclass
class Signal:
    source: str
    value: float              # Normalized score in [-1, 1]
    confidence: float         # [0, 1]
    trend: str                # IMPROVING / DECLINING / STABLE
    regime: str = "NORMAL"    # NORMAL / VOLATILE
    trust_weight: float = 0.0
    note: str = ""

@dataclass
class FusionResult:
    score: float
    confidence: float
    direction: str
    agreement: float
    instability: float
