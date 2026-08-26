import pandas as pd


class ATRIndicator:

    def calculate(
        self,
        candles,
        period=14,
    ):

        df = pd.DataFrame(candles)

        high = df["high"]
        low = df["low"]
        close = df["close"]

        previous_close = close.shift(1)

        tr = pd.concat(
            [
                high - low,
                (high - previous_close).abs(),
                (low - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr = tr.rolling(
            window=period,
        ).mean()

        return atr.fillna(0).tolist()