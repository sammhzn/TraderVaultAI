from dataclasses import dataclass

from app.ai.mistake_analyzer import MistakeAnalyzer


@dataclass
class FakeTrade:
    result: str
    profit: float


def test_analyzer_counts_wins_and_losses():

    trades = [
        FakeTrade("WIN", 20.0),
        FakeTrade("WIN", 30.0),
        FakeTrade("LOSS", -10.0),
        FakeTrade("LOSS", -15.0),
    ]

    analyzer = MistakeAnalyzer()

    summary = analyzer.analyze(trades)

    assert summary.total_trades == 4
    assert summary.winning_trades == 2
    assert summary.losing_trades == 2


def test_analyzer_calculates_profit_and_loss():

    trades = [
        FakeTrade("WIN", 50.0),
        FakeTrade("WIN", 25.0),
        FakeTrade("LOSS", -20.0),
        FakeTrade("LOSS", -15.0),
    ]

    analyzer = MistakeAnalyzer()

    summary = analyzer.analyze(trades)

    assert summary.total_profit == 75.0
    assert summary.total_loss == 35.0


def test_losing_trades_returns_only_losses():

    trades = [
        FakeTrade("WIN", 50.0),
        FakeTrade("LOSS", -20.0),
        FakeTrade("WIN", 10.0),
        FakeTrade("LOSS", -5.0),
    ]

    analyzer = MistakeAnalyzer()

    losses = analyzer.losing_trades(trades)

    assert len(losses) == 2
    assert all(trade.result == "LOSS" for trade in losses)


def test_winning_trades_returns_only_wins():

    trades = [
        FakeTrade("WIN", 50.0),
        FakeTrade("LOSS", -20.0),
        FakeTrade("WIN", 10.0),
    ]

    analyzer = MistakeAnalyzer()

    wins = analyzer.winning_trades(trades)

    assert len(wins) == 2
    assert all(trade.result == "WIN" for trade in wins)