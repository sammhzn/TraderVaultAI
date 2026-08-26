from app.backtesting.trade_simulator import TradeSimulator
from app.trade.tp1_manager import TP1Manager


class TradeLifecycle:

    def __init__(self):
        self.simulator = TradeSimulator()
        self.tp1 = TP1Manager()

    def open_trade(
        self,
        direction,
        entry,
        stop_loss,
        take_profit,
        layer=1,
    ):
        return self.simulator.open_trade(
            direction,
            entry,
            stop_loss,
            take_profit,
            layer,
        )

    def tp1_hit(self):
        return self.tp1.manage(
            self.simulator,
            close_layers=2,
        )

    def active_trades(self):
        return self.simulator.active_trades()