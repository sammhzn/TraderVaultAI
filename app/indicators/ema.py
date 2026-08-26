import pandas as pd


class EMAIndicator:

    def calculate(
        self,
        candles,
        period=20,
    ):
        """
        Calculate EMA for a list of candles.

        candles:
            list of dicts containing:
            open, high, low, close

        Returns:
            list of EMA values
        """

        closes = [c["close"] for c in candles]

        series = pd.Series(closes)

        ema = series.ewm(
            span=period,
            adjust=False,
        ).mean()

        return ema.tolist()