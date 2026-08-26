from app.backtesting.strategy_replay import StrategyReplay


def test_strategy_replay_creation():

    replay = StrategyReplay()

    assert replay is not None