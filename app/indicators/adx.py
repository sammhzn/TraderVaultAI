import pandas as pd


class ADXIndicator:

    def calculate(
        self,
        candles,
        period=14,
    ):

        df = pd.DataFrame(candles)

        high = df["high"]
        low = df["low"]
        close = df["close"]

        previous_high = high.shift(1)
        previous_low = low.shift(1)
        previous_close = close.shift(1)

        plus_dm = previous_high
        minus_dm = previous_low

        plus_dm = high - previous_high
        minus_dm = previous_low - low

        plus_dm = plus_dm.where(
            (plus_dm > minus_dm) & (plus_dm > 0),
            0,
        )

        minus_dm = minus_dm.where(
            (minus_dm > plus_dm) & (minus_dm > 0),
            0,
        )

        true_range = pd.concat(
            [
                high - low,
                (high - previous_close).abs(),
                (low - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr = true_range.rolling(
            window=period
        ).mean()

        plus_di = (
            100
            * plus_dm.rolling(window=period).mean()
            / atr
        )

        minus_di = (
            100
            * minus_dm.rolling(window=period).mean()
            / atr
        )

        denominator = plus_di + minus_di

        dx = (
            100
            * (plus_di - minus_di).abs()
            / denominator
        )

        adx = dx.rolling(
            window=period
        ).mean()

        return {
            "adx": adx.fillna(0).tolist(),
            "plus_di": plus_di.fillna(0).tolist(),
            "minus_di": minus_di.fillna(0).tolist(),
        }