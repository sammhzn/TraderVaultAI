from app.database.database import get_session
from app.database.models import Trade


class TradeRepository:

    def __init__(self):
        self.session = get_session()

    def save_trade(
        self,
        symbol,
        timeframe,
        strategy,
        trade,
    ):

        db_trade = Trade(
            symbol=symbol,
            timeframe=timeframe,
            strategy=strategy,
            direction=trade.direction,
            entry=trade.entry,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            layer=trade.layer,
            open_time=trade.open_time,
            close_time=trade.close_time,
            result=trade.result,
            profit=trade.profit,
        )

        self.session.add(db_trade)
        self.session.commit()

    def get_all_trades(self):

        return (
            self.session
            .query(Trade)
            .order_by(Trade.id.desc())
            .all()
        )

    def delete_all_trades(self):

        self.session.query(Trade).delete()
        self.session.commit()

    def close(self):

        self.session.close()