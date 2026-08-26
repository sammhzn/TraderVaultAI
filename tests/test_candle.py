from datetime import datetime

from app.core.candle import Candle


def test_bullish_candle():

    candle = Candle(
        time=datetime.now(),
        open=4080.00,
        high=4081.00,
        low=4079.80,
        close=4080.60,
    )

    assert candle.bullish
    assert not candle.bearish


def test_bearish_candle():

    candle = Candle(
        time=datetime.now(),
        open=4080.60,
        high=4080.80,
        low=4079.50,
        close=4079.70,
    )

    assert candle.bearish
    assert not candle.bullish


def test_body_size():

    candle = Candle(
        time=datetime.now(),
        open=4080.00,
        high=4081.00,
        low=4079.00,
        close=4080.50,
    )

    assert candle.body_size == 0.50