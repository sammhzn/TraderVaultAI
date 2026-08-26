from dataclasses import dataclass

from app.core.candle import Candle


@dataclass
class MarketContext:
    """
    Holds all information needed by the Strategy Engine
    for one incoming candle.
    """

    current_candle: Candle

    previous_day_high: float

    previous_day_low: float