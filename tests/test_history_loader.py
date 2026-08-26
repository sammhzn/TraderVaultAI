from app.backtesting.history_loader import HistoryLoader


def test_history_loader():

    loader = HistoryLoader()

    assert loader is not None