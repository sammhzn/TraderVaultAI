from app.backtesting.candle_executor import CandleExecutor
from app.backtesting.trade_simulator import TradeSimulator


def test_take_profit_hit():

    simulator = TradeSimulator()

    simulator.open_trade(
        direction="BUY",
        entry=4080.00,
        stop_loss=4079.50,
        take_profit=4082.00,
    )

    candle = {
        "high": 4082.20,
        "low": 4079.90,
    }

    executor = CandleExecutor()

    closed = executor.process_candle(
        candle,
        simulator,
    )

    assert closed == 1
    assert len(simulator.active_trades()) == 0