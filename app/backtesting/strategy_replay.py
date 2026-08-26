from datetime import datetime

from app.engine.trading_engine import TradingEngine
from app.models.market_context import MarketContext
from app.core.candle import Candle
from app.backtesting.daily_level_calculator import DailyLevelCalculator


class StrategyReplay:

    def __init__(self):

        self.engine = TradingEngine()
        self.levels = DailyLevelCalculator()

    def replay(
            self,
            candles,
            config=None,
    ):

        decisions = []

        daily_levels = self.levels.calculate(candles)

        for row in candles:

            day = datetime.fromtimestamp(row["time"]).date()

            if day not in daily_levels:
                continue

            previous_high, previous_low = daily_levels[day]

            candle = Candle(
                time=datetime.fromtimestamp(row["time"]),
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["tick_volume"],
            )

            context = MarketContext(
                current_candle=candle,
                previous_day_high=previous_high,
                previous_day_low=previous_low,
            )

            decision = self.engine.process_market(
                context,
                config=config,
            )

            decisions.append(decision)

        return decisions