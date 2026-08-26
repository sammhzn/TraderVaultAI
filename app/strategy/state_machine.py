from enum import Enum


class StrategyState(Enum):
    WAITING_FOR_SWEEP = "WAITING_FOR_SWEEP"
    WAITING_FOR_SIGNAL = "WAITING_FOR_SIGNAL"
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    READY_TO_ENTER = "READY_TO_ENTER"
    TRADE_OPEN = "TRADE_OPEN"
    MANAGING_LAYERS = "MANAGING_LAYERS"
    TP1_REACHED = "TP1_REACHED"
    BREAKEVEN = "BREAKEVEN"
    TRADE_CLOSED = "TRADE_CLOSED"


class StrategyStateMachine:
    """
    Controls the current state of the strategy.
    """

    def __init__(self):
        self.state = StrategyState.WAITING_FOR_SWEEP

    def transition(self, new_state: StrategyState):
        self.state = new_state

    def current_state(self):
        return self.state