from dataclasses import dataclass
from typing import Any


@dataclass
class MistakeSummary:
    total_trades: int
    losing_trades: int
    winning_trades: int
    total_loss: float
    total_profit: float


class MistakeAnalyzer:
    """
    Analyzes completed trades and summarizes losing outcomes.

    This component does not change the strategy.
    It only identifies and measures mistakes so that
    later components can learn from them.
    """

    def analyze(
        self,
        trades: list[Any],
    ) -> MistakeSummary:

        losing_trades = [
            trade
            for trade in trades
            if trade.result == "LOSS"
        ]

        winning_trades = [
            trade
            for trade in trades
            if trade.result == "WIN"
        ]

        total_loss = abs(
            sum(
                float(trade.profit)
                for trade in losing_trades
            )
        )

        total_profit = sum(
            float(trade.profit)
            for trade in winning_trades
        )

        return MistakeSummary(
            total_trades=len(trades),
            losing_trades=len(losing_trades),
            winning_trades=len(winning_trades),
            total_loss=total_loss,
            total_profit=total_profit,
        )

    def losing_trades(
        self,
        trades: list[Any],
    ) -> list[Any]:

        return [
            trade
            for trade in trades
            if trade.result == "LOSS"
        ]

    def winning_trades(
        self,
        trades: list[Any],
    ) -> list[Any]:

        return [
            trade
            for trade in trades
            if trade.result == "WIN"
        ]