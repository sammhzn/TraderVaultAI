from dataclasses import dataclass

from app.models.market_context import MarketContext
from app.strategy.confirmation import ConfirmationEngine
from app.strategy.liquidity import LiquidityEngine
from app.strategy.signal import SignalEngine
from app.strategy.state_machine import StrategyState
from app.strategy.strategy_session import StrategySession


@dataclass
class StrategyDecision:
    action: str
    reason: str


class StrategyEngine:

    def __init__(self):
        self.session = StrategySession()

    def evaluate(
        self,
        context: MarketContext,
        config=None,
    ):

        candle = context.current_candle

        # --------------------------------------------------
        # Start / reset session for a new trading day
        # --------------------------------------------------

        self.session.new_day(
            candle.time.date()
        )

        state = self.session.state_machine.current_state()

        # ==================================================
        # WAITING FOR LIQUIDITY SWEEP
        # ==================================================

        if state == StrategyState.WAITING_FOR_SWEEP:

            # --------------------------------------------------
            # Check previous day HIGH for SELL sweep
            # --------------------------------------------------

            if not self.session.pdh_used:

                sell = LiquidityEngine.detect_sell_sweep(
                    candle,
                    context.previous_day_high,
                )

                if sell.valid:

                    self.session.sweep_direction = "SELL"

                    self.session.state_machine.transition(
                        StrategyState.WAITING_FOR_SIGNAL
                    )

                    return StrategyDecision(
                        action="WAIT_SIGNAL",
                        reason=sell.reason,
                    )

            # --------------------------------------------------
            # Check previous day LOW for BUY sweep
            # --------------------------------------------------

            if not self.session.pdl_used:

                buy = LiquidityEngine.detect_buy_sweep(
                    candle,
                    context.previous_day_low,
                )

                if buy.valid:

                    self.session.sweep_direction = "BUY"

                    self.session.state_machine.transition(
                        StrategyState.WAITING_FOR_SIGNAL
                    )

                    return StrategyDecision(
                        action="WAIT_SIGNAL",
                        reason=buy.reason,
                    )

            return StrategyDecision(
                action="NO_TRADE",
                reason="Waiting for sweep",
            )

        # ==================================================
        # WAITING FOR SIGNAL CANDLE
        # ==================================================

        elif state == StrategyState.WAITING_FOR_SIGNAL:

            # --------------------------------------------------
            # SELL setup
            # After PDH sweep, wait for first bearish candle
            # --------------------------------------------------

            if self.session.sweep_direction == "SELL":

                signal = SignalEngine.detect_sell_signal(
                    candle
                )

            # --------------------------------------------------
            # BUY setup
            # After PDL sweep, wait for first bullish candle
            # --------------------------------------------------

            else:

                signal = SignalEngine.detect_buy_signal(
                    candle
                )

            if signal.found:

                self.session.signal_candle = candle

                self.session.state_machine.transition(
                    StrategyState.WAITING_FOR_CONFIRMATION
                )

                return StrategyDecision(
                    action="WAIT_CONFIRMATION",
                    reason=signal.reason,
                )

            return StrategyDecision(
                action="WAIT_SIGNAL",
                reason="Waiting for signal candle",
            )

        # ==================================================
        # WAITING FOR CONFIRMATION
        # ==================================================

        elif state == StrategyState.WAITING_FOR_CONFIRMATION:

            signal_candle = self.session.signal_candle

            # Safety check
            if signal_candle is None:

                self.session.reset()

                return StrategyDecision(
                    action="RESET",
                    reason="Missing signal candle",
                )

            # --------------------------------------------------
            # SELL confirmation
            # --------------------------------------------------

            if self.session.sweep_direction == "SELL":

                confirmation = ConfirmationEngine.confirm_sell(
                    signal_candle,
                    candle,
                )

            # --------------------------------------------------
            # BUY confirmation
            # --------------------------------------------------

            else:

                confirmation = ConfirmationEngine.confirm_buy(
                    signal_candle,
                    candle,
                )

            # --------------------------------------------------
            # Confirmation successful
            # --------------------------------------------------

            if confirmation.confirmed:

                self.session.mark_sweep_used()

                self.session.state_machine.transition(
                    StrategyState.READY_TO_ENTER
                )

                return StrategyDecision(
                    action="READY_TO_ENTER",
                    reason=confirmation.reason,
                )

            # --------------------------------------------------
            # Confirmation failed
            # --------------------------------------------------

            self.session.reset()

            return StrategyDecision(
                action="RESET",
                reason="Confirmation failed. Waiting for new sweep.",
            )

        # ==================================================
        # READY TO ENTER
        # ==================================================

        elif state == StrategyState.READY_TO_ENTER:

            return StrategyDecision(
                action="ENTER_TRADE",
                reason="Trade is ready.",
            )

        # ==================================================
        # FALLBACK
        # ==================================================

        return StrategyDecision(
            action="NO_ACTION",
            reason="Unknown strategy state.",
        )