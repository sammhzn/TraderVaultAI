from datetime import datetime

from app.backtesting.history_loader import HistoryLoader
from app.backtesting.strategy_replay import StrategyReplay
from app.backtesting.performance import PerformanceAnalyzer
from app.database.repository import TradeRepository
from app.ai.feature_extractor import FeatureExtractor
from app.ai.dataset_builder import DatasetBuilder


class BacktestRunner:

    def __init__(self):
        self.loader = HistoryLoader()
        self.replay = StrategyReplay()
        self.performance = PerformanceAnalyzer()
        self.repository = TradeRepository()
        self.feature_extractor = FeatureExtractor()
        self.dataset_builder = DatasetBuilder()

    def run(
        self,
        symbol="XAUUSD",
        timeframe=None,
        bars=1000,
        config=None,
        persist=True,
    ):

        candles = self.loader.load(
            symbol=symbol,
            timeframe=timeframe,
            bars=bars,
        )

        decisions = self.replay.replay(
            candles,
            config=config,
        )

        simulator = self.replay.engine.simulator

        # --------------------------------------------------
        # Calculate daily liquidity levels
        # --------------------------------------------------

        daily_levels = self.replay.levels.calculate(
            candles
        )

        # --------------------------------------------------
        # Process completed trades
        # --------------------------------------------------

        for trade in simulator.trades:

            if trade.result == "OPEN":
                continue

            # --------------------------------------------------
            # Save trade and AI features only when requested.
            #
            # Normal backtests:
            #     persist=True
            #
            # Research experiments:
            #     persist=False
            # --------------------------------------------------

            if persist:

                self.repository.save_trade(
                    symbol=symbol,
                    timeframe=str(timeframe),
                    strategy="Liquidity Sweep",
                    trade=trade,
                )

                # --------------------------------------------------
                # Determine the trading day of this trade
                # --------------------------------------------------

                previous_day_high = 0
                previous_day_low = 0

                if trade.open_time is not None:

                    trade_day = (
                        trade.open_time.date()
                    )

                    if trade_day in daily_levels:

                        (
                            previous_day_high,
                            previous_day_low,
                        ) = daily_levels[trade_day]

                # --------------------------------------------------
                # Prevent look-ahead bias
                #
                # Only candles available at trade entry
                # are used.
                # --------------------------------------------------

                historical_candles = []

                if trade.open_time is not None:

                    for candle in candles:

                        candle_time = (
                            datetime.fromtimestamp(
                                candle["time"]
                            )
                        )

                        if (
                            candle_time
                            <= trade.open_time
                        ):
                            historical_candles.append(
                                candle
                            )

                # --------------------------------------------------
                # Build AI features
                # --------------------------------------------------

                features = (
                    self.feature_extractor.extract(
                        symbol=symbol,
                        strategy="Liquidity Sweep",
                        trade=trade,
                        previous_day_high=(
                            previous_day_high
                        ),
                        previous_day_low=(
                            previous_day_low
                        ),
                        candles=historical_candles,
                    )
                )

                self.dataset_builder.add(
                    features
                )

        # --------------------------------------------------
        # Performance report
        # --------------------------------------------------

        report = self.performance.analyze(
            wins=simulator.total_wins(),
            losses=simulator.total_losses(),
            gross_profit=simulator.gross_profit(),
            gross_loss=simulator.gross_loss(),
            net_profit=simulator.net_profit(),
            profit_factor=simulator.profit_factor(),
        )

        # --------------------------------------------------
        # Export AI training dataset only for normal
        # persistent backtests.
        # --------------------------------------------------

        if persist:
            self.dataset_builder.export_csv()

        return {
            "candles": len(candles),
            "decisions": len(decisions),
            "positions": simulator.open_trade_count(),
            "report": report,
        }