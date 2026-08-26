from dataclasses import dataclass

from app.core.candle import Candle


@dataclass
class ConfirmationResult:
    confirmed: bool
    direction: str
    reason: str


class ConfirmationEngine:

    @staticmethod
    def confirm_sell(
        signal_candle: Candle,
        confirmation_candle: Candle,
    ):

        if confirmation_candle.close < signal_candle.low:
            return ConfirmationResult(
                confirmed=True,
                direction="SELL",
                reason="Confirmation candle closed below signal candle low",
            )

        return ConfirmationResult(
            confirmed=False,
            direction="NONE",
            reason="Sell confirmation failed",
        )

    @staticmethod
    def confirm_buy(
        signal_candle: Candle,
        confirmation_candle: Candle,
    ):

        if confirmation_candle.close > signal_candle.high:
            return ConfirmationResult(
                confirmed=True,
                direction="BUY",
                reason="Confirmation candle closed above signal candle high",
            )

        return ConfirmationResult(
            confirmed=False,
            direction="NONE",
            reason="Buy confirmation failed",
        )