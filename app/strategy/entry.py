from dataclasses import dataclass


@dataclass
class EntrySignal:
    direction: str
    entry_price: float
    stop_loss: float
    valid: bool
    reason: str


class EntryDetector:
    """
    Confirms trade entry after the signal candle.
    """

    def detect(
        self,
        trade_direction: str,
        signal_open: float,
        signal_close: float,
        signal_high: float,
        signal_low: float,
        current_close: float,
    ) -> EntrySignal:

        # SELL
        if trade_direction == "SELL":

            signal_body_low = min(signal_open, signal_close)

            if current_close < signal_body_low:
                return EntrySignal(
                    direction="SELL",
                    entry_price=current_close,
                    stop_loss=signal_high,
                    valid=True,
                    reason="Closed below signal candle body",
                )

        # BUY
        if trade_direction == "BUY":

            signal_body_high = max(signal_open, signal_close)

            if current_close > signal_body_high:
                return EntrySignal(
                    direction="BUY",
                    entry_price=current_close,
                    stop_loss=signal_low,
                    valid=True,
                    reason="Closed above signal candle body",
                )

        return EntrySignal(
            direction="NONE",
            entry_price=0.0,
            stop_loss=0.0,
            valid=False,
            reason="Entry not confirmed",
        )