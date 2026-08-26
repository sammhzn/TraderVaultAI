import MetaTrader5 as mt5


class HistoryLoader:

    def load(
        self,
        symbol="XAUUSD",
        timeframe=mt5.TIMEFRAME_M1,
        bars=1000,
    ):
        """
        Load historical candle data from MetaTrader 5.

        Returns:
            MT5 rates array containing OHLCV candle data.
        """

        # Initialize MT5
        if not mt5.initialize():
            raise RuntimeError(
                f"MT5 initialization failed: {mt5.last_error()}"
            )

        try:
            # Load historical candles
            rates = mt5.copy_rates_from_pos(
                symbol,
                timeframe,
                0,
                bars,
            )

            # Check whether MT5 returned data
            if rates is None:
                raise RuntimeError(
                    f"Failed to load historical data: {mt5.last_error()}"
                )

            return rates

        finally:
            # Always close the MT5 connection
            mt5.shutdown()