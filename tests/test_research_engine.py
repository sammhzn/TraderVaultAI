from dataclasses import dataclass

from app.ai.research_engine import ResearchEngine


@dataclass
class FakeReport:
    total_trades: int
    wins: int
    losses: int
    gross_profit: float
    gross_loss: float
    net_profit: float
    profit_factor: float


def fake_backtest(config):
    rr = config["rr"]

    if rr >= 4:
        return FakeReport(
            total_trades=20,
            wins=12,
            losses=8,
            gross_profit=120.0,
            gross_loss=40.0,
            net_profit=80.0,
            profit_factor=3.0,
        )

    return FakeReport(
        total_trades=20,
        wins=7,
        losses=13,
        gross_profit=70.0,
        gross_loss=100.0,
        net_profit=-30.0,
        profit_factor=0.70,
    )


def test_research_engine_creates_all_experiments():

    engine = ResearchEngine(
        backtest_function=fake_backtest
    )

    parameters = {
        "rsi_period": [10, 14],
        "rr": [2, 4],
    }

    experiments = engine.create_experiments(
        parameters
    )

    assert len(experiments) == 4


def test_research_engine_runs_all_experiments():

    engine = ResearchEngine(
        backtest_function=fake_backtest
    )

    parameters = {
        "rsi_period": [10, 14],
        "rr": [2, 4],
    }

    research_run = engine.run(parameters)

    assert len(research_run.experiments) == 4
    assert len(research_run.results) == 4


def test_research_engine_finds_best_result():

    engine = ResearchEngine(
        backtest_function=fake_backtest
    )

    parameters = {
        "rsi_period": [10, 14],
        "rr": [2, 4],
    }

    research_run = engine.run(parameters)

    assert research_run.best_result is not None
    assert research_run.best_result.net_profit == 80.0


def test_research_engine_identifies_profitable_results():

    engine = ResearchEngine(
        backtest_function=fake_backtest
    )

    parameters = {
        "rsi_period": [10, 14],
        "rr": [2, 4],
    }

    research_run = engine.run(parameters)

    assert len(research_run.profitable_results) == 2

    for result in research_run.profitable_results:
        assert result.net_profit > 0