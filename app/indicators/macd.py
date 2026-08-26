import pandas as pd


class MACDIndicator:

    def calculate(self, candles):

        closes = pd.Series(
            [c["close"] for c in candles]
        )

        ema12 = closes.ewm(
            span=12,
            adjust=False,
        ).mean()

        ema26 = closes.ewm(
            span=26,
            adjust=False,
        ).mean()

        macd = ema12 - ema26

        signal = macd.ewm(
            span=9,
            adjust=False,
        ).mean()

        histogram = macd - signal

        return {
            "macd": macd.fillna(0).tolist(),
            "signal": signal.fillna(0).tolist(),
            "histogram": histogram.fillna(0).tolist(),
        }