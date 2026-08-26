from app.backtesting.equity_curve import EquityCurve


def test_equity_curve():

    curve = EquityCurve(starting_balance=10000)

    curve.record_trade(150)
    curve.record_trade(-50)

    assert curve.latest_balance() == 10100

    assert len(curve.points) == 3