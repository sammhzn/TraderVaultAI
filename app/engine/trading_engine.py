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

    # --------------------------------------------------
    # Configuration helper
    # --------------------------------------------------

    @staticmethod
    def _config_value(
        config,
        name,
        default=None,
    ):
        """
        Read a configuration value from either:

        1. A normal dictionary
        2. A configuration object

        This keeps the trading engine compatible with
        both the existing strategy system and the new
        research/parameter-search system.
        """

        if config is None:
            return default

        if isinstance(config, dict):
            return config.get(
                name,
                default,
            )

        return getattr(
            config,
            name,
            default,
        )

    def process_market(
        self,
        market_context,
        config=None,
    ):

        # --------------------------------------------------
        # Update all open simulated trades
        # --------------------------------------------------

        self.simulator.update_trades(
            market_context.current_candle
        )

        # --------------------------------------------------
        # Evaluate strategy
        # --------------------------------------------------

        decision = self.strategy.evaluate(
            market_context,
            config=config,
        )

        # --------------------------------------------------
        # Log decision
        # --------------------------------------------------

        self.journal.log(
            "STRATEGY",
            decision.reason,
        )

        # --------------------------------------------------
        # Open trade if strategy enters
        # --------------------------------------------------

        if decision.action == "ENTER_TRADE":

            # --------------------------------------------------
            # Layering configuration
            # --------------------------------------------------

            layering = self._config_value(
                config,
                "layering",
                None,
            )

            max_layers = self._config_value(
                config,
                "max_layers",
                5,
            )

            # --------------------------------------------------
            # Layering OFF
            #
            # Only one open trade allowed.
            # --------------------------------------------------

            if (
                layering is False
                and self.simulator.open_trade_count() > 0
            ):
                return decision

            # --------------------------------------------------
            # Layering ON
            #
            # Respect maximum number of layers.
            # --------------------------------------------------

            if (
                layering is True
                and self.simulator.open_trade_count()
                >= max_layers
            ):
                return decision

            # --------------------------------------------------
            # Determine trade direction
            # --------------------------------------------------

            direction = (
                self.strategy.session.sweep_direction
            )

            candle = (
                market_context.current_candle
            )

            signal_candle = (
                self.strategy.session.signal_candle
            )

            # --------------------------------------------------
            # Safety check
            # --------------------------------------------------

            if signal_candle is None:

                self.journal.log(
                    "TRADE",
                    "Entry rejected: missing signal candle",
                )

                return decision

            # --------------------------------------------------
            # Stop Loss
            #
            # BUY  -> signal candle LOW
            # SELL -> signal candle HIGH
            # --------------------------------------------------

            if direction == "BUY":
                stop_loss = signal_candle.low
            else:
                stop_loss = signal_candle.high

            # --------------------------------------------------
            # Save trade
            # --------------------------------------------------

            self.trade_manager.open_trade(
                direction=direction,
                entry=candle.close,
                stop_loss=stop_loss,
                layer=1,
            )

            # --------------------------------------------------
            # Risk
            # --------------------------------------------------

            risk = abs(
                candle.close - stop_loss
            )

            # --------------------------------------------------
            # Risk : Reward
            #
            # ResearchEngine uses "rr".
            #
            # Existing configuration may use
            # "risk_reward".
            #
            # Support both.
            # --------------------------------------------------

            rr = self._config_value(
                config,
                "risk_reward",
                None,
            )

            if rr is None:
                rr = self._config_value(
                    config,
                    "rr",
                    2,
                )

            rr = float(rr)

            # --------------------------------------------------
            # Take Profit
            # --------------------------------------------------

            if direction == "BUY":

                take_profit = (
                    candle.close
                    + (risk * rr)
                )

            else:

                take_profit = (
                    candle.close
                    - (risk * rr)
                )

            # --------------------------------------------------
            # Simulated trade
            # --------------------------------------------------

            self.simulator.open_trade(
                direction=direction,
                entry=candle.close,
                stop_loss=stop_loss,
                take_profit=take_profit,
                layer=1,
                open_time=candle.time,
            )

            # --------------------------------------------------
            # Reset strategy after opening trade
            # --------------------------------------------------

            self.strategy.session.reset()

            self.journal.log(
                "TRADE",
                f"{direction} opened @ {candle.close:.2f}",
            )

        return decision