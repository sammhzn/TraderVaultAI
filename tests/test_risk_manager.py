from app.risk.risk_manager import RiskManager


def test_position_size():

    manager = RiskManager()

    result = manager.calculate_position_size(
        balance=10000,
        risk_percent=1,
        stop_loss_points=20,
    )

    assert result.risk_amount == 100
    assert result.lot_size == 5