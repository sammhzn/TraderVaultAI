from app.trade.trade_manager import Position, TradeManager


def test_tp1_management():

    manager = TradeManager()

    manager.positions = [

        Position(1, "BUY", 4080.00, 4079.50),

        Position(2, "BUY", 4079.80, 4079.30),

        Position(3, "BUY", 4079.60, 4079.10),
    ]

    manager.close_tp1()

    # Layer 3 should now be inactive
    assert manager.positions[2].active is False

    # Remaining positions move SL to breakeven
    assert manager.positions[0].stop_loss == 4080.00
    assert manager.positions[1].stop_loss == 4079.80

    # Only two active positions remain
    assert len(manager.active_positions()) == 2