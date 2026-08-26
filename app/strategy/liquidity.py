from dataclasses import dataclass

from app.core.candle import Candle


@dataclass
class LiquiditySweep:
    valid: bool
    direction: str
    level: float
    reason: str


class LiquidityEngine:

    @staticmethod
    def detect_sell_sweep(
        candle: Candle,
        previous_day_high: float,
    ) -> LiquiditySweep:

        if (
            candle.open > previous_day_high
            and candle.close > previous_day_high
        ):
            return LiquiditySweep(
                valid=True,
                direction="SELL",
                level=previous_day_high,
                reason="Full candle body closed above PDH",
            )

        return LiquiditySweep(
            valid=False,
            direction="NONE",
            level=previous_day_high,
            reason="No valid sell liquidity sweep",
        )

    @staticmethod
    def detect_buy_sweep(
        candle: Candle,
        previous_day_low: float,
    ) -> LiquiditySweep:

        if (
            candle.open < previous_day_low
            and candle.close < previous_day_low
        ):
            return LiquiditySweep(
                valid=True,
                direction="BUY",
                level=previous_day_low,
                reason="Full candle body closed below PDL",
            )

        return LiquiditySweep(
            valid=False,
            direction="NONE",
            level=previous_day_low,
            reason="No valid buy liquidity sweep",
        )