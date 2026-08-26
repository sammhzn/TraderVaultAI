from app.indicators.ema import EMAIndicator
from app.indicators.rsi import RSIIndicator
from app.indicators.atr import ATRIndicator
from app.indicators.macd import MACDIndicator
from app.indicators.adx import ADXIndicator
from app.indicators.bollinger import BollingerBandsIndicator


def sample_candles(count=100):

    candles = []

    price = 3300.0

    for i in range(count):

        open_price = price
        close_price = price + (0.5 if i % 2 == 0 else -0.2)

        high = max(open_price, close_price) + 1
        low = min(open_price, close_price) - 1

        candles.append(
            {
                "time": i,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close_price,
                "tick_volume": 1000,
            }
        )

        price = close_price

    return candles


def test_ema():

    candles = sample_candles()

    result = EMAIndicator().calculate(
        candles,
        period=20,
    )

    assert len(result) == len(candles)
    assert all(isinstance(x, float) for x in result)


def test_rsi():

    candles = sample_candles()

    result = RSIIndicator().calculate(
        candles,
        period=14,
    )

    assert len(result) == len(candles)

    assert all(
        0 <= x <= 100
        for x in result
    )


def test_atr():

    candles = sample_candles()

    result = ATRIndicator().calculate(
        candles,
        period=14,
    )

    assert len(result) == len(candles)

    assert all(
        x >= 0
        for x in result
    )


def test_macd():

    candles = sample_candles()

    result = MACDIndicator().calculate(
        candles
    )

    assert "macd" in result
    assert "signal" in result
    assert "histogram" in result

    assert len(result["macd"]) == len(candles)
    assert len(result["signal"]) == len(candles)
    assert len(result["histogram"]) == len(candles)


def test_adx():

    candles = sample_candles()

    result = ADXIndicator().calculate(
        candles,
        period=14,
    )

    assert "adx" in result
    assert "plus_di" in result
    assert "minus_di" in result

    assert len(result["adx"]) == len(candles)
    assert len(result["plus_di"]) == len(candles)
    assert len(result["minus_di"]) == len(candles)

    assert all(
        x >= 0
        for x in result["adx"]
    )


def test_bollinger():

    candles = sample_candles()

    result = BollingerBandsIndicator().calculate(
        candles,
        period=20,
    )

    assert "middle" in result
    assert "upper" in result
    assert "lower" in result
    assert "width" in result

    assert len(result["middle"]) == len(candles)
    assert len(result["upper"]) == len(candles)
    assert len(result["lower"]) == len(candles)
    assert len(result["width"]) == len(candles)

    assert all(
        x >= 0
        for x in result["width"]
    )