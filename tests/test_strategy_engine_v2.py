from datetime import datetime

from app.core.candle import Candle
from app.models.market_context import MarketContext
from app.strategy.strategy_engine import StrategyEngine


def test_detect_sell_sweep():

    candle = Candle(
        time=datetime.now(),
        open=4080.20,
        high=4080.40,
        low=4079.90,
        close=4080.10,
    )

    context = MarketContext(
        current_candle=candle,
        previous_day_high=4080.00,
        previous_day_low=4070.00,
    )

    decision = StrategyEngine().evaluate(context)

    assert decision.action == "WAIT_SIGNAL"


def test_no_setup():

    candle = Candle(
        time=datetime.now(),
        open=4078.50,
        high=4078.80,
        low=4078.20,
        close=4078.40,
    )

    context = MarketContext(
        current_candle=candle,
        previous_day_high=4080.00,
        previous_day_low=4070.00,
    )

    decision = StrategyEngine().evaluate(context)

    assert decision.action == "NO_TRADE"