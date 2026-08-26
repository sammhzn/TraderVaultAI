from collections import defaultdict
from datetime import datetime


class DailyLevelCalculator:

    def calculate(self, candles):

        daily = defaultdict(list)

        for candle in candles:

            day = datetime.fromtimestamp(candle["time"]).date()

            daily[day].append(candle)

        ordered_days = sorted(daily.keys())

        levels = {}

        for i in range(1, len(ordered_days)):

            previous = ordered_days[i - 1]
            current = ordered_days[i]

            previous_candles = daily[previous]

            high = max(c["high"] for c in previous_candles)
            low = min(c["low"] for c in previous_candles)

            levels[current] = (
                high,
                low,
            )

        return levels