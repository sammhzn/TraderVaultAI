import pandas as pd


class RSIIndicator:

    def calculate(
        self,
        candles,
        period=14,
    ):
        closes = pd.Series(
            [c["close"] for c in candles]
        )

        delta = closes.diff()

        gain = delta.where(
            delta > 0,
            0,
        )

        loss = -delta.where(
            delta < 0,
            0,
        )

        avg_gain = gain.rolling(
            window=period,
        ).mean()

        avg_loss = loss.rolling(
            window=period,
        ).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (
            100 / (1 + rs)
        )

        return rsi.fillna(50).tolist()