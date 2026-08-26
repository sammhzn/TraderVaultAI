from app.trade.position_manager import (
    ManagedPosition,
    PositionManager,
)


def test_position_manager():

    manager = PositionManager()

    manager.add(
        ManagedPosition(
            ticket=1,
            layer=1,
            direction="BUY",
            entry_price=4080.00,
            stop_loss=4079.50,
            take_profit=4082.00,
        )
    )

    manager.add(
        ManagedPosition(
            ticket=2,
            layer=2,
            direction="BUY",
            entry_price=4079.80,
            stop_loss=4079.30,
            take_profit=4082.00,
        )
    )

    assert manager.count() == 2

    assert manager.newest().layer == 2