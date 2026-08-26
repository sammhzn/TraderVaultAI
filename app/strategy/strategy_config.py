from dataclasses import dataclass


@dataclass
class StrategyConfig:
    risk_percent: float = 1.0
    risk_reward: int = 2
    max_layers: int = 5
    break_even: bool = True
    layering: bool = True