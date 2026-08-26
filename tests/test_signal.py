from datetime import datetime

from app.core.candle import Candle
from app.strategy.signal import SignalEngine


def test_sell_signal():

    candle = Candle(
        time=datetime.now(),
        open=4080.30,
        high=4080.40,
        low=4079.80,
        close=4079.90,
    )

    result = SignalEngine.detect_sell_signal(candle)

    assert result.found
    assert result.direction == "SELL"


def test_buy_signal():

    candle = Candle(
        time=datetime.now(),
        open=4070.00,
        high=4070.50,
        low=4069.90,
        close=4070.40,
    )

    result = SignalEngine.detect_buy_signal(candle)

    assert result.found
    assert result.direction == "BUY"


def test_invalid_sell_signal():

    candle = Candle(
        time=datetime.now(),
        open=4079.80,
        high=4080.20,
        low=4079.70,
        close=4080.10,
    )

    result = SignalEngine.detect_sell_signal(candle)

    assert not result.found


def test_invalid_buy_signal():

    candle = Candle(
        time=datetime.now(),
        open=4070.30,
        high=4070.40,
        low=4069.80,
        close=4070.00,
    )

    result = SignalEngine.detect_buy_signal(candle)

    assert not result.found