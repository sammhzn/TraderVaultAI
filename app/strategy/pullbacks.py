from dataclasses import dataclass


@dataclass
class PullbackResult:
    valid: bool
    reason: str
    allow_layer: bool


class PullbackDetector:
    """
    Detects whether market structure allows
    an additional layer.
    """

    def detect(
        self,
        trade_direction: str,
        current_price: float,
        first_entry: float,
        layers_open: int,
        max_layers: int = 5,
        max_distance: float = 1.00,
    ) -> PullbackResult:

        # Already at maximum layers
        if layers_open >= max_layers:
            return PullbackResult(
                valid=False,
                allow_layer=False,
                reason="Maximum layers reached",
            )

        # BUY logic
        if trade_direction == "BUY":

            distance = first_entry - current_price

            if distance > max_distance:
                return PullbackResult(
                    valid=False,
                    allow_layer=False,
                    reason="Exceeded maximum pullback distance",
                )

            return PullbackResult(
                valid=True,
                allow_layer=True,
                reason="BUY pullback within limits",
            )

        # SELL logic
        if trade_direction == "SELL":

            distance = current_price - first_entry

            if distance > max_distance:
                return PullbackResult(
                    valid=False,
                    allow_layer=False,
                    reason="Exceeded maximum pullback distance",
                )

            return PullbackResult(
                valid=True,
                allow_layer=True,
                reason="SELL pullback within limits",
            )

        return PullbackResult(
            valid=False,
            allow_layer=False,
            reason="Unknown trade direction",
        )