from app.trade.tp1_manager import TP1Manager
from app.backtesting.trade_simulator import TradeSimulator


def test_tp1():

    sim = TradeSimulator()

    sim.open_trade(
        "BUY",
        4080,
        4079.5,
        4082,
        layer=1,
    )

    sim.open_trade(
        "BUY",
        4079.8,
        4079.3,
        4082,
        layer=2,
    )

    sim.open_trade(
        "BUY",
        4079.6,
        4079.1,
        4082,
        layer=3,
    )

    manager = TP1Manager()

    active = manager.manage(
        sim,
        close_layers=2,
    )

    assert len(active) == 1
    assert active[0].layer == 1
    assert active[0].break_even