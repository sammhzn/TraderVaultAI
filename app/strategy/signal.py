from dataclasses import dataclass

from app.core.candle import Candle


@dataclass
class SignalResult:
    found: bool
    direction: str
    candle: Candle | None
    reason: str


class SignalEngine:
    """
    Finds the first opposite-colored candle after a liquidity sweep.
    """

    @staticmethod
    def detect_sell_signal(candle: Candle) -> SignalResult:

        if candle.bearish:
            return SignalResult(
                found=True,
                direction="SELL",
                candle=candle,
                reason="First bearish candle detected",
            )

        return SignalResult(
            found=False,
            direction="NONE",
            candle=None,
            reason="No bearish signal candle",
        )

    @staticmethod
    def detect_buy_signal(candle: Candle) -> SignalResult:

        if candle.bullish:
            return SignalResult(
                found=True,
                direction="BUY",
                candle=candle,
                reason="First bullish signal candle detected",
            )

        return SignalResult(
            found=False,
            direction="NONE",
            candle=None,
            reason="No bullish signal candle",
        )