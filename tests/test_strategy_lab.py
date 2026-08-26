from app.ai.strategy_lab import (
    StrategyLab,
    StrategyExperiment,
)


def test_add_experiment():
    lab = StrategyLab()

    experiment = lab.add_experiment(
        name="RSI Baseline",
        strategy="RSI Divergence",
        parameters={
            "rsi_period": 14,
            "rr": 4.0,
        },
    )

    assert isinstance(experiment, StrategyExperiment)
    assert experiment.name == "RSI Baseline"
    assert experiment.strategy == "RSI Divergence"
    assert experiment.parameters["rsi_period"] == 14


def test_add_result_calculates_win_rate():
    lab = StrategyLab()

    experiment = lab.add_experiment(
        name="Test",
        strategy="RSI Divergence",
    )

    result = lab.add_result(
        experiment=experiment,
        total_trades=100,
        wins=40,
        losses=60,
        gross_profit=160.0,
        gross_loss=120.0,
        net_profit=40.0,
        profit_factor=1.3333,
    )

    assert result.win_rate == 0.40
    assert result.net_profit == 40.0


def test_best_profit_factor():
    lab = StrategyLab()

    weak = lab.add_experiment(
        name="Weak",
        strategy="RSI Divergence",
    )

    strong = lab.add_experiment(
        name="Strong",
        strategy="RSI Divergence",
    )

    lab.add_result(
        weak,
        100,
        30,
        70,
        100.0,
        150.0,
        -50.0,
        0.67,
    )

    lab.add_result(
        strong,
        100,
        45,
        55,
        180.0,
        120.0,
        60.0,
        1.50,
    )

    best = lab.best_by_profit_factor()

    assert best is not None
    assert best.experiment.name == "Strong"


def test_profitable_results():
    lab = StrategyLab()

    profitable = lab.add_experiment(
        name="Profitable",
        strategy="RSI Divergence",
    )

    losing = lab.add_experiment(
        name="Losing",
        strategy="RSI Divergence",
    )

    lab.add_result(
        profitable,
        100,
        45,
        55,
        180.0,
        120.0,
        60.0,
        1.50,
    )

    lab.add_result(
        losing,
        100,
        30,
        70,
        100.0,
        150.0,
        -50.0,
        0.67,
    )

    results = lab.profitable_results()

    assert len(results) == 1
    assert results[0].experiment.name == "Profitable"
