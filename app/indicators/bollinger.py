import pandas as pd


class BollingerBandsIndicator:

    def calculate(
        self,
        candles,
        period=20,
        std_dev=2,
    ):

        closes = pd.Series(
            [c["close"] for c in candles]
        )

        middle = closes.rolling(
            window=period
        ).mean()

        standard_deviation = closes.rolling(
            window=period
        ).std()

        upper = (
            middle
            + std_dev * standard_deviation
        )

        lower = (
            middle
            - std_dev * standard_deviation
        )

        width = upper - lower

        return {
            "middle": middle.fillna(0).tolist(),
            "upper": upper.fillna(0).tolist(),
            "lower": lower.fillna(0).tolist(),
            "width": width.fillna(0).tolist(),
        }