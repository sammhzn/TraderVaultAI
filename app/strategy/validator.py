from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    action: str
    reason: str


class StrategyValidator:
    """
    Combines all strategy components
    into one trading decision.
    """

    def validate(
        self,
        liquidity_valid: bool,
        signal_valid: bool,
        entry_valid: bool,
        pullback_valid: bool,
    ) -> ValidationResult:

        if not liquidity_valid:
            return ValidationResult(
                valid=False,
                action="NO TRADE",
                reason="Liquidity sweep invalid",
            )

        if not signal_valid:
            return ValidationResult(
                valid=False,
                action="NO TRADE",
                reason="Signal candle missing",
            )

        if not entry_valid:
            return ValidationResult(
                valid=False,
                action="NO TRADE",
                reason="Entry not confirmed",
            )

        if not pullback_valid:
            return ValidationResult(
                valid=False,
                action="NO TRADE",
                reason="Pullback rules failed",
            )

        return ValidationResult(
            valid=True,
            action="EXECUTE",
            reason="All strategy rules passed",
        )