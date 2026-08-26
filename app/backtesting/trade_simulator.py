from dataclasses import dataclass
from datetime import datetime


@dataclass
class SimulatedTrade:
    direction: str
    entry: float
    stop_loss: float
    take_profit: float
    layer: int

    open_time: datetime = None
    close_time: datetime = None

    active: bool = True
    break_even: bool = False
    result: str = "OPEN"

    profit: float = 0.0


class TradeSimulator:

    def __init__(self):
        self.trades = []
        
    def open_trade(
        self,
        direction,
        entry,
        stop_loss,
        take_profit,
        layer=1,
        open_time=None,
    ):

        trade = SimulatedTrade(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            layer=layer,
            open_time=open_time,
        )

        self.trades.append(trade)

        return trade

    def active_trades(self):

        return [
            trade
            for trade in self.trades
            if trade.active
        ]

    def move_to_break_even(self):

        for trade in self.active_trades():
            trade.stop_loss = trade.entry
            trade.break_even = True

    def close_newest_layers(
        self,
        count=2,
    ):

        active = sorted(
            self.active_trades(),
            key=lambda x: x.layer,
            reverse=True,
        )

        for trade in active[:count]:
            trade.active = False
            trade.result = "TP1"
            trade.close_time = datetime.now()

    def update_trades(
            self,
            candle,
    ):

        for trade in self.active_trades():

            risk = abs(
                trade.entry - trade.stop_loss
            )

            if trade.direction == "BUY":

                # Stop Loss
                if candle.low <= trade.stop_loss:
                    trade.active = False
                    trade.result = "LOSS"
                    trade.profit = -risk
                    trade.close_time = candle.time

                # Take Profit
                elif candle.high >= trade.take_profit:
                    trade.active = False
                    trade.result = "WIN"
                    trade.profit = (
                            trade.take_profit
                            - trade.entry
                    )
                    trade.close_time = candle.time

            else:

                # Stop Loss
                if candle.high >= trade.stop_loss:
                    trade.active = False
                    trade.result = "LOSS"
                    trade.profit = -risk
                    trade.close_time = candle.time

                # Take Profit
                elif candle.low <= trade.take_profit:
                    trade.active = False
                    trade.result = "WIN"
                    trade.profit = (
                            trade.entry
                            - trade.take_profit
                    )
                    trade.close_time = candle.time
                    
    def total_trades(self):

        return len(self.trades)

    def total_wins(self):

        return len(
            [
                trade
                for trade in self.trades
                if trade.result == "WIN"
            ]
        )

    def total_losses(self):

        return len(
            [
                trade
                for trade in self.trades
                if trade.result == "LOSS"
            ]
        )

    def open_trade_count(self):

        return len(
            self.active_trades()
        )

    def gross_profit(self):

        return round(
            sum(
                trade.profit
                for trade in self.trades
                if trade.profit > 0
            ),
            2,
        )

    def gross_loss(self):

        return round(
            abs(
                sum(
                    trade.profit
                    for trade in self.trades
                    if trade.profit < 0
                )
            ),
            2,
        )

    def net_profit(self):

        return round(
            sum(
                trade.profit
                for trade in self.trades
            ),
            2,
        )

    def profit_factor(self):

        loss = self.gross_loss()

        if loss == 0:
            return 0.0

        return round(
            self.gross_profit() / loss,
            2,
        )