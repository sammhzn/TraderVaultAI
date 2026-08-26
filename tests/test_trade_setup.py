from datetime import datetime

from app.models.trade_setup import TradeSetup


def test_trade_setup():

    trade = TradeSetup(
        id="TV-0001",
        created_at=datetime.now(),
        direction="BUY",
        state="READY",
        sweep_level="PDL",
    )

    assert trade.direction == "BUY"

    assert trade.layers == 1

    assert trade.state == "READY"