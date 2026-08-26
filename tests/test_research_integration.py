from app.ai.research_engine import ResearchEngine


def fake_backtest(config):
    rr = config["rr"]

    if rr == 4:
        return {
            "total_trades": 20,
            "wins": 14,
            "losses": 6,
            "net_profit": 250.0,
            "profit_factor": 2.0,
        }

    return {
        "total_trades": 20,
        "wins": 8,
        "losses": 12,
        "net_profit": -100.0,
        "profit_factor": 0.8,
    }


def test_research_engine_runs_parameter_search():

    engine = ResearchEngine(
        backtest_function=fake_backtest
    )

    research_run = engine.run(
        {
            "rsi_period": [10, 14],
            "rr": [2, 4],
        }
    )

    assert len(research_run.experiments) == 4
    assert len(research_run.results) == 4

    assert research_run.best_result is not None
    assert research_run.best_result.net_profit == 250.0

    assert len(
        research_run.profitable_results
    ) == 2