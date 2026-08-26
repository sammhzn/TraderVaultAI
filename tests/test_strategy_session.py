from app.strategy.state_machine import (
    StrategyState,
    StrategyStateMachine,
)
from app.strategy.strategy_session import StrategySession


def test_session_reset():

    session = StrategySession(
        state_machine=StrategyStateMachine()
    )

    session.state_machine.transition(
        StrategyState.WAITING_FOR_SIGNAL
    )

    session.signal_candle = "dummy"

    session.reset()

    assert (
        session.state_machine.current_state()
        == StrategyState.WAITING_FOR_SWEEP
    )

    assert session.signal_candle is None