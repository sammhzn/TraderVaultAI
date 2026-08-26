import MetaTrader5 as mt5


class HistoryLoader:

    def load(
        self,
        symbol="XAUUSD",
        timeframe=mt5.TIMEFRAME_M1,
        bars=1000,
    ):

        # Initialize MT5
        if not mt5.initialize():
            print("❌ MT5 initialization failed")
            print("Error:", mt5.last_error())
            return []

        # Make sure the symbol is available
        if not mt5.symbol_select(symbol, True):
            print(f"❌ Cannot select symbol: {symbol}")
            mt5.shutdown()
            return []

        # Load historical candles
        data = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            0,
            bars,
        )

        # Shut down MT5 connection
        mt5.shutdown()

        if data is None:
            print("❌ No historical data returned")
            return []

        # Convert MT5 structured array into dictionaries
        candles = []

        for row in data:

            candles.append({
                "time": row["time"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "tick_volume": int(row["tick_volume"]),
                "spread": int(row["spread"]),
                "real_volume": int(row["real_volume"]),
            })

        return candles