from app.backtesting.performance import PerformanceAnalyzer


def test_performance():

    analyzer = PerformanceAnalyzer()

    report = analyzer.analyze(
        wins=7,
        losses=3,
        gross_profit=1400.0,
        gross_loss=700.0,
        net_profit=700.0,
        profit_factor=2.0,
    )

    assert report.total_trades == 10
    assert report.wins == 7
    assert report.losses == 3
    assert report.win_rate == 70.0

    assert report.gross_profit == 1400.0
    assert report.gross_loss == 700.0
    assert report.net_profit == 700.0
    assert report.profit_factor == 2.0