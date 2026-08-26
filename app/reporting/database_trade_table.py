import pandas as pd

from app.database.repository import TradeRepository


class DatabaseTradeTable:

    def __init__(self):
        self.repository = TradeRepository()

    def build(self):

        trades = self.repository.get_all_trades()

        rows = []

        for trade in trades:

            rows.append(
                {
                    "ID": trade.id,
                    "Symbol": trade.symbol,
                    "Strategy": trade.strategy,
                    "Direction": trade.direction,
                    "Entry": round(trade.entry, 2),
                    "SL": round(trade.stop_loss, 2),
                    "TP": round(trade.take_profit, 2),
                    "Profit": round(trade.profit, 2),
                    "Result": trade.result,
                    "Layer": trade.layer,
                    "Open Time": trade.open_time,
                    "Close Time": trade.close_time,
                }
            )

        return pd.DataFrame(rows)