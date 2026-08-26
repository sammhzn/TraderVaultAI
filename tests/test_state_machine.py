from app.strategy.state_machine import (
    StrategyState,
    StrategyStateMachine,
)


def test_initial_state():

    machine = StrategyStateMachine()

    assert machine.current_state() == StrategyState.WAITING_FOR_SWEEP


def test_transition():

    machine = StrategyStateMachine()

    machine.transition(StrategyState.WAITING_FOR_SIGNAL)

    assert machine.current_state() == StrategyState.WAITING_FOR_SIGNAL