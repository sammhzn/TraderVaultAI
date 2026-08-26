from app.backtesting.backtest_engine import BacktestEngine


def test_backtest():

    candles = [

        {"close": 4080},

        {"close": 4081},

        {"close": 4082},

    ]

    engine = BacktestEngine()

    result = engine.run(candles)

    assert result.candles_processed == 3