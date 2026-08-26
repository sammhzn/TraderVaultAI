import pandas as pd


class TradeTable:

    def build(self, trades):

        rows = []

        for trade in trades:

            rows.append(
                {
                    "Time": trade.open_time,
                    "Direction": trade.direction,
                    "Entry": round(trade.entry, 2),
                    "Stop Loss": round(trade.stop_loss, 2),
                    "Take Profit": round(trade.take_profit, 2),
                    "Layer": trade.layer,
                    "Result": trade.result,
                    "Profit": round(trade.profit, 2),
                    "Break Even": trade.break_even,
                    "Active": trade.active,
                    "Close Time": trade.close_time,
                }
            )

        return pd.DataFrame(rows)