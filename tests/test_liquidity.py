from datetime import datetime

from app.core.candle import Candle
from app.strategy.liquidity import LiquidityEngine


def test_valid_sell_sweep():

    candle = Candle(
        time=datetime.now(),
        open=4080.10,
        high=4080.40,
        low=4079.80,
        close=4080.20,
    )

    result = LiquidityEngine.detect_sell_sweep(
        candle,
        4080.00,
    )

    assert result.valid
    assert result.direction == "SELL"


def test_valid_buy_sweep():

    candle = Candle(
        time=datetime.now(),
        open=4069.90,
        high=4070.20,
        low=4069.60,
        close=4069.80,
    )

    result = LiquidityEngine.detect_buy_sweep(
        candle,
        4070.00,
    )

    assert result.valid
    assert result.direction == "BUY"


def test_invalid_sell_sweep():

    candle = Candle(
        time=datetime.now(),
        open=4079.90,
        high=4080.50,
        low=4079.70,
        close=4079.80,
    )

    result = LiquidityEngine.detect_sell_sweep(
        candle,
        4080.00,
    )

    assert not result.valid


def test_invalid_buy_sweep():

    candle = Candle(
        time=datetime.now(),
        open=4070.10,
        high=4070.30,
        low=4069.80,
        close=4070.05,
    )

    result = LiquidityEngine.detect_buy_sweep(
        candle,
        4070.00,
    )

    assert not result.valid