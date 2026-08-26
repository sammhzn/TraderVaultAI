from datetime import datetime

from app.core.candle import Candle
from app.models.market_context import MarketContext
from app.strategy.strategy_engine import StrategyEngine


def test_strategy_engine_default():

    engine = StrategyEngine()

    candle = Candle(
        time=datetime.now(),
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.5,
    )

    context = MarketContext(
        current_candle=candle,
        previous_day_high=110.0,
        previous_day_low=90.0,
    )

    decision = engine.evaluate(context)

    assert decision.action == "NO_TRADE"