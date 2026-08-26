from app.ai.experiment_runner import (
    Experiment,
    ExperimentResult,
    ExperimentRunner,
)


def fake_backtest(config):
    return {
        "total_trades": config["trades"],
        "wins": config["wins"],
        "losses": config["losses"],
        "net_profit": config["profit"],
        "profit_factor": config["profit_factor"],
    }


def test_experiment_creation():
    experiment = Experiment(
        name="Test Strategy",
        config={"trades": 10},
    )

    assert experiment.name == "Test Strategy"
    assert experiment.config["trades"] == 10


def test_run_single_experiment():
    runner = ExperimentRunner(
        backtest_function=fake_backtest
    )

    experiment = Experiment(
        name="Strategy A",
        config={
            "trades": 20,
            "wins": 12,
            "losses": 8,
            "profit": 100.0,
            "profit_factor": 1.5,
        },
    )

    result = runner.run_experiment(experiment)

    assert isinstance(result, ExperimentResult)
    assert result.experiment.name == "Strategy A"
    assert result.total_trades == 20
    assert result.wins == 12
    assert result.losses == 8
    assert result.net_profit == 100.0
    assert result.profit_factor == 1.5


def test_run_all_experiments():
    runner = ExperimentRunner(
        backtest_function=fake_backtest
    )

    experiments = [
        Experiment(
            name="Strategy A",
            config={
                "trades": 10,
                "wins": 6,
                "losses": 4,
                "profit": 50.0,
                "profit_factor": 1.2,
            },
        ),
        Experiment(
            name="Strategy B",
            config={
                "trades": 15,
                "wins": 10,
                "losses": 5,
                "profit": 120.0,
                "profit_factor": 1.8,
            },
        ),
    ]

    results = runner.run_all(experiments)

    assert len(results) == 2
    assert results[0].experiment.name == "Strategy A"
    assert results[1].experiment.name == "Strategy B"


def test_best_result():
    runner = ExperimentRunner(
        backtest_function=fake_backtest
    )

    experiments = [
        Experiment(
            name="Bad Strategy",
            config={
                "trades": 20,
                "wins": 5,
                "losses": 15,
                "profit": -100.0,
                "profit_factor": 0.5,
            },
        ),
        Experiment(
            name="Good Strategy",
            config={
                "trades": 20,
                "wins": 12,
                "losses": 8,
                "profit": 200.0,
                "profit_factor": 1.8,
            },
        ),
    ]

    runner.run_all(experiments)

    best = runner.best_result()

    assert best is not None
    assert best.experiment.name == "Good Strategy"
    assert best.net_profit == 200.0


def test_profitable_results():
    runner = ExperimentRunner(
        backtest_function=fake_backtest
    )

    experiments = [
        Experiment(
            name="Losing",
            config={
                "trades": 10,
                "wins": 3,
                "losses": 7,
                "profit": -50.0,
                "profit_factor": 0.7,
            },
        ),
        Experiment(
            name="Profitable",
            config={
                "trades": 10,
                "wins": 7,
                "losses": 3,
                "profit": 80.0,
                "profit_factor": 1.6,
            },
        ),
    ]

    runner.run_all(experiments)

    results = runner.profitable_results()

    assert len(results) == 1
    assert results[0].experiment.name == "Profitable"