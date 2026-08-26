from app.strategy.strategy_engine import StrategyEngine
from app.strategy.entry import EntryDetector
from app.strategy.layer_manager import LayerManager
from app.trade.trade_manager import TradeManager
from app.trade.position_manager import PositionManager
from app.journal.trade_journal import TradeJournal
from app.backtesting.trade_simulator import TradeSimulator


class TradingEngine:

    def __init__(self):

        self.strategy = StrategyEngine()
        self.entry = EntryDetector()
        self.layers = LayerManager()
        self.trade_manager = TradeManager()
        self.positions = PositionManager()
        self.journal = TradeJournal()
        self.simulator = TradeSimulator()

    def process_market(
        self,
        market_context,
        config=None,
    ):

        # Update all open simulated trades
        self.simulator.update_trades(
            market_context.current_candle
        )

        # Evaluate strategy
        decision = self.strategy.evaluate(
            market_context,
            config=config,
        )

        # Log decision
        self.journal.log(
            "STRATEGY",
            decision.reason,
        )

        # Open trade if strategy enters
        if decision.action == "ENTER_TRADE":

            # Layering OFF -> only one open trade allowed
            if config is not None and not config.layering:
                if self.simulator.open_trade_count() > 0:
                    return decision

            # Layering ON -> obey maximum layers
            if config is not None and config.layering:
                if self.simulator.open_trade_count() >= config.max_layers:
                    return decision
            direction = self.strategy.session.sweep_direction
            candle = market_context.current_candle
            signal_candle = self.strategy.session.signal_candle

            # The stop must come from the original signal candle,
            # not the confirmation/entry candle.
            if signal_candle is None:
                self.journal.log(
                    "TRADE",
                    "Entry rejected: missing signal candle",
                )
                return decision

            if direction == "BUY":
                stop_loss = signal_candle.low
            else:
                stop_loss = signal_candle.high
            # Save trade
            self.trade_manager.open_trade(
                direction=direction,
                entry=candle.close,
                stop_loss=stop_loss,
                layer=1,
            )

            # Risk
            risk = abs(candle.close - stop_loss)

            # Risk : Reward
            rr = 2
            if config is not None:
                rr = config.risk_reward

            # Take Profit
            if direction == "BUY":
                take_profit = candle.close + (risk * rr)
            else:
                take_profit = candle.close - (risk * rr)

            # Simulated trade
            self.simulator.open_trade(
                direction=direction,
                entry=candle.close,
                stop_loss=stop_loss,
                take_profit=take_profit,
                layer=1,
                open_time=candle.time,
            )

            # Reset strategy after opening trade
            self.strategy.session.reset()
            
            self.journal.log(
                "TRADE",
                f"{direction} opened @ {candle.close:.2f}",
            )

        return decision