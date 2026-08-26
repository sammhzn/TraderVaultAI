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

        # SELL:
        # Confirmation candle must close below
        # the BODY of the bearish signal candle.
        signal_body_low = min(
            signal_candle.open,
            signal_candle.close,
        )

        if confirmation_candle.close < signal_body_low:
            return ConfirmationResult(
                confirmed=True,
                direction="SELL",
                reason="Confirmation candle closed below signal candle body",
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

        # BUY:
        # Confirmation candle must close above
        # the BODY of the bullish signal candle.
        signal_body_high = max(
            signal_candle.open,
            signal_candle.close,
        )

        if confirmation_candle.close > signal_body_high:
            return ConfirmationResult(
                confirmed=True,
                direction="BUY",
                reason="Confirmation candle closed above signal candle body",
            )

        return ConfirmationResult(
            confirmed=False,
            direction="NONE",
            reason="Buy confirmation failed",
        )