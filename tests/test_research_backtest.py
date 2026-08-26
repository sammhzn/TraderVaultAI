import app.ai.research_backtest as research_backtest_module


class FakeBacktestRunner:

    def __init__(self):
        self.calls = []

    def run(
        self,
        symbol,
        timeframe,
        bars,
        config,
        persist,
    ):
        self.calls.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "bars": bars,
                "config": config,
                "persist": persist,
            }
        )

        return {
            "total_trades": 10,
            "wins": 6,
            "losses": 4,
            "net_profit": 100.0,
            "profit_factor": 1.5,
        }


def test_research_backtest_calls_real_backtest_interface(
    monkeypatch,
):
    monkeypatch.setattr(
        research_backtest_module,
        "BacktestRunner",
        FakeBacktestRunner,
    )

    adapter = research_backtest_module.ResearchBacktest(
        symbol="XAUUSD",
        bars=500,
    )

    config = {
        "rr": 4,
    }

    result = adapter.run(config)

    assert result["total_trades"] == 10
    assert result["wins"] == 6
    assert result["losses"] == 4
    assert result["net_profit"] == 100.0
    assert result["profit_factor"] == 1.5