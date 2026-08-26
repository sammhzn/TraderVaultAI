from dataclasses import dataclass


@dataclass
class BacktestResult:
    candles_processed: int
    trades: int


class BacktestEngine:

    def run(self, candles):

        processed = 0

        for candle in candles:
            processed += 1

        return BacktestResult(
            candles_processed=processed,
            trades=0,
        )