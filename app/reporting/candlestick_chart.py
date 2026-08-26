print(">>> NEW candlestick_chart.py loaded <<<")
import pandas as pd
import plotly.graph_objects as go


class CandlestickChart:

    def build(
            self,
            candles,
            trades=None,
            previous_day_high=None,
            previous_day_low=None,
    ):

        rows = []

        for c in candles:
            rows.append(
                {
                    "time": c["time"],
                    "open": c["open"],
                    "high": c["high"],
                    "low": c["low"],
                    "close": c["close"],
                }
            )

        df = pd.DataFrame(rows)

        fig = go.Figure()

        fig.add_trace(
            go.Candlestick(
                x=pd.to_datetime(df["time"], unit="s"),
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                increasing_line_color="green",
                decreasing_line_color="red",
                name="Price",
            )
        )
        # ==========================================
        # Previous Day High / Low
        # ==========================================

        if previous_day_high is not None:
            fig.add_hline(
                y=previous_day_high,
                line_color="gold",
                line_dash="dash",
                annotation_text="Previous Day High",
                annotation_position="top left",
            )

        if previous_day_low is not None:
            fig.add_hline(
                y=previous_day_low,
                line_color="cyan",
                line_dash="dash",
                annotation_text="Previous Day Low",
                annotation_position="bottom left",
            )

        if trades:

            buy_x = []
            buy_y = []

            sell_x = []
            sell_y = []

            for trade in trades:

                if trade.open_time is None:
                    continue

                # Entry line
                fig.add_shape(
                    type="line",
                    x0=trade.open_time,
                    x1=trade.open_time,
                    y0=trade.stop_loss,
                    y1=trade.take_profit,
                    line=dict(
                        color="white",
                        width=1,
                        dash="dot",
                    ),
                )

                # Stop Loss
                fig.add_trace(
                    go.Scatter(
                        x=[trade.open_time],
                        y=[trade.stop_loss],
                        mode="markers",
                        marker=dict(
                            color="red",
                            size=8,
                            symbol="x",
                        ),
                        showlegend=False,
                    )
                )

                # Take Profit
                fig.add_trace(
                    go.Scatter(
                        x=[trade.open_time],
                        y=[trade.take_profit],
                        mode="markers",
                        marker=dict(
                            color="dodgerblue",
                            size=8,
                            symbol="circle",
                        ),
                        showlegend=False,
                    )
                )

                if trade.direction == "BUY":
                    buy_x.append(pd.to_datetime(trade.open_time))
                    buy_y.append(trade.entry)
                else:
                    sell_x.append(pd.to_datetime(trade.open_time))
                    sell_y.append(trade.entry)
                    if trade.close_time is not None:

                        if trade.result == "WIN":
                            color = "lime"
                        elif trade.result == "LOSS":
                            color = "red"
                        else:
                            color = "yellow"
                            
                        fig.add_trace(
                            go.Scatter(
                                x=[trade.open_time, trade.close_time],
                                y=[trade.entry, trade.take_profit if trade.result == "WIN" else trade.stop_loss],
                                mode="lines",
                                line=dict(
                                    color=color,
                                    width=3,
                                ),
                                showlegend=False,
                            )
                        )

            go.Scatter(
                x=buy_x,
                y=buy_y,
                mode="markers",
                marker=dict(
                    color="lime",
                    size=10,
                    symbol="triangle-up",
                ),
                name="BUY",
                text=[
                    f"""
            BUY
            Entry : {t.entry:.2f}
            SL : {t.stop_loss:.2f}
            TP : {t.take_profit:.2f}
            Result : {t.result}
            Profit : {t.profit:.2f}
            Layer : {t.layer}
            """
                    for t in trades
                    if t.direction == "BUY"
                ],
                hovertemplate="%{text}<extra></extra>",
            )

            go.Scatter(
                x=sell_x,
                y=sell_y,
                mode="markers",
                marker=dict(
                    color="red",
                    size=10,
                    symbol="triangle-down",
                ),
                name="SELL",
                text=[
                    f"""
            SELL
            Entry : {t.entry:.2f}
            SL : {t.stop_loss:.2f}
            TP : {t.take_profit:.2f}
            Result : {t.result}
            Profit : {t.profit:.2f}
            Layer : {t.layer}
            """
                    for t in trades
                    if t.direction == "SELL"
                ],
                hovertemplate="%{text}<extra></extra>",
            )

        fig.update_layout(
            title="TraderVaultAI Chart",
            template="plotly_dark",
            xaxis_title="Time",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            height=700,
        )

        return fig