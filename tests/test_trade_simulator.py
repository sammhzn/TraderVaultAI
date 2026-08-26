from app.backtesting.trade_simulator import (
    TradeSimulator,
)


def test_tp1_management():

    sim = TradeSimulator()

    sim.open_trade(
        "BUY",
        4080.00,
        4079.50,
        4082.00,
        layer=1,
    )

    sim.open_trade(
        "BUY",
        4079.80,
        4079.30,
        4082.00,
        layer=2,
    )

    sim.open_trade(
        "BUY",
        4079.60,
        4079.10,
        4082.00,
        layer=3,
    )

    sim.close_newest_layers(count=1)

    assert len(sim.active_trades()) == 2

    sim.move_to_break_even()

    assert sim.active_trades()[0].break_even