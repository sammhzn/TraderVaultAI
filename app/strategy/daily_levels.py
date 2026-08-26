from dataclasses import dataclass


@dataclass
class DailyLevels:
    previous_day_high: float
    previous_day_low: float
    current_day_high: float
    current_day_low: float
    asian_high: float
    asian_low: float
    london_high: float
    london_low: float
    newyork_high: float
    newyork_low: float


class DailyLevelEngine:
    """
    Stores and manages important market levels.
    Price calculation from candles will be added later.
    """

    def __init__(self):
        self.levels = DailyLevels(
            previous_day_high=0.0,
            previous_day_low=0.0,
            current_day_high=0.0,
            current_day_low=0.0,
            asian_high=0.0,
            asian_low=0.0,
            london_high=0.0,
            london_low=0.0,
            newyork_high=0.0,
            newyork_low=0.0,
        )

    def get_levels(self):
        return self.levels

    def update_level(self, name: str, value: float):
        if hasattr(self.levels, name):
            setattr(self.levels, name, value)