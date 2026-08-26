from app.journal.trade_journal import TradeJournal


def test_trade_journal():

    journal = TradeJournal()

    journal.log(
        "ENTRY",
        "BUY opened",
    )

    journal.log(
        "TP1",
        "Closed newest layer",
    )

    assert journal.count() == 2

    assert journal.latest().event == "TP1"