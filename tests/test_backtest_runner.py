from app.backtesting.backtest_runner import BacktestRunner


def test_runner_creation():

    runner = BacktestRunner()

    assert runner is not None