from datetime import datetime

from app.core.candle import Candle
from app.models.market_context import MarketContext
from app.replay.replay_engine import ReplayEngine


def test_replay_runs():

    replay = ReplayEngine()

    candle = Candle(
        time=datetime.now(),
        open=100,
        high=101,
        low=99,
        close=100,
    )

    context = MarketContext(
        current_candle=candle,
        previous_day_high=110,
        previous_day_low=90,
    )

    decisions = replay.replay([context])

    assert len(decisions) == 1