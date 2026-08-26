import csv


class TradeExporter:

    def export(
        self,
        trades,
        filename="trade_history.csv",
    ):

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Direction",
                "Entry",
                "Stop Loss",
                "Take Profit",
                "Layer",
                "Result",
                "Profit",
            ])

            for trade in trades:

                writer.writerow([
                    trade.direction,
                    trade.entry,
                    trade.stop_loss,
                    trade.take_profit,
                    trade.layer,
                    trade.result,
                    trade.profit,
                ])

        return filename