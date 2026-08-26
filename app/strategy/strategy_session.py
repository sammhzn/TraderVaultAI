from dataclasses import dataclass, field
from datetime import date

from app.strategy.state_machine import (
    StrategyState,
    StrategyStateMachine,
)


@dataclass
class StrategySession:

    state_machine: StrategyStateMachine = field(
        default_factory=StrategyStateMachine
    )

    signal_candle: object | None = None
    sweep_direction: str | None = None
    trade_setup: object | None = None

    # -----------------------------
    # Daily liquidity protection
    # -----------------------------
    current_day: date | None = None
    pdh_used: bool = False
    pdl_used: bool = False

    # -----------------------------
    # Level arming
    # -----------------------------
    pdh_armed: bool = False
    pdl_armed: bool = False

    def new_day(self, trading_day: date):

        if self.current_day != trading_day:

            self.current_day = trading_day

            self.pdh_used = False
            self.pdl_used = False

            self.pdh_armed = False
            self.pdl_armed = False

            self.reset()

    def update_level_arming(
        self,
        close: float,
        previous_day_high: float,
        previous_day_low: float,
    ):

        # Price must first be on/below PDH before
        # a move above PDH can be treated as a fresh sweep.
        if close <= previous_day_high:
            self.pdh_armed = True

        # Price must first be on/above PDL before
        # a move below PDL can be treated as a fresh sweep.
        if close >= previous_day_low:
            self.pdl_armed = True

    def mark_sweep_used(self):

        if self.sweep_direction == "SELL":
            self.pdh_used = True
            self.pdh_armed = False

        elif self.sweep_direction == "BUY":
            self.pdl_used = True
            self.pdl_armed = False

    def reset(self):

        self.state_machine.transition(
            StrategyState.WAITING_FOR_SWEEP
        )

        self.signal_candle = None
        self.sweep_direction = None
        self.trade_setup = None