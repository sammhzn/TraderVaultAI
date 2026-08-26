from app.trade.trade_lifecycle import TradeLifecycle


def test_trade_lifecycle():

    lifecycle = TradeLifecycle()

    lifecycle.open_trade(
        "BUY",
        4080.00,
        4079.50,
        4082.00,
        layer=1,
    )

    lifecycle.open_trade(
        "BUY",
        4079.80,
        4079.30,
        4082.00,
        layer=2,
    )

    lifecycle.open_trade(
        "BUY",
        4079.60,
        4079.10,
        4082.00,
        layer=3,
    )

    active = lifecycle.tp1_hit()

    assert len(active) == 1
    assert active[0].layer == 1
    assert active[0].break_even