import pandas as pd
import plotly.graph_objects as go


class TradePlotter:

    def add_trades(
        self,
        figure,
        trades,
    ):

        buy_x = []
        buy_y = []

        sell_x = []
        sell_y = []

        for trade in trades:

            if not hasattr(trade, "time"):
                continue

            if trade.direction == "BUY":
                buy_x.append(trade.time)
                buy_y.append(trade.entry)

            else:
                sell_x.append(trade.time)
                sell_y.append(trade.entry)

        if buy_x:

            figure.add_trace(

                go.Scatter(

                    x=buy_x,
                    y=buy_y,

                    mode="markers",

                    name="BUY",

                    marker=dict(
                        color="lime",
                        size=10,
                        symbol="triangle-up",
                    ),
                )
            )

        if sell_x:

            figure.add_trace(

                go.Scatter(

                    x=sell_x,
                    y=sell_y,

                    mode="markers",

                    name="SELL",

                    marker=dict(
                        color="red",
                        size=10,
                        symbol="triangle-down",
                    ),
                )
            )

        return figure