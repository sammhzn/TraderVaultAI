import MetaTrader5 as mt5


class MarketDataService:

    def latest_tick(self, symbol="XAUUSD"):
        return mt5.symbol_info_tick(symbol)

    def latest_candle(self, symbol="XAUUSD", timeframe=mt5.TIMEFRAME_M1):

        candles = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            0,
            1,
        )

        if candles is None:
            return None

        return candles[0]