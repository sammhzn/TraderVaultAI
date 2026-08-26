from typing import Any, Dict

import MetaTrader5 as mt5

from app.backtesting.backtest_runner import BacktestRunner


class ResearchBacktest:

    def __init__(
        self,
        symbol: str = "XAUUSD",
        timeframe: int = mt5.TIMEFRAME_M1,
        bars: int = 1000,
    ):
        self.symbol = symbol
        self.timeframe = timeframe
        self.bars = bars

    def run(
        self,
        config: Dict[str, Any],
    ):
        """
        Run one research experiment through the real
        BacktestRunner.

        Each experiment uses a fresh BacktestRunner,
        StrategyReplay, TradingEngine, and simulator.

        Research experiments do not save trades to the
        database and do not modify the AI training dataset.
        """

        runner = BacktestRunner()

        result = runner.run(
            symbol=self.symbol,
            timeframe=self.timeframe,
            bars=self.bars,
            config=config,
            persist=False,
        )

        # --------------------------------------------------
        # Real BacktestRunner
        #
        # The real runner returns a dictionary containing
        # the PerformanceReport under "report".
        # --------------------------------------------------

        if isinstance(result, dict):

            report = result.get("report")

            if report is not None:
                return report

        # --------------------------------------------------
        # Test/fake runners or alternative backtest
        # implementations may return the performance result
        # directly.
        # --------------------------------------------------

        return result