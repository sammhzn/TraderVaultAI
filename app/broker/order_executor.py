import MetaTrader5 as mt5


class OrderExecutor:

    def __init__(self):
        pass

    def market_buy(
        self,
        symbol: str,
        volume: float,
        stop_loss: float,
        take_profit: float,
    ):

        tick = mt5.symbol_info_tick(symbol)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 20,
            "magic": 123456,
            "comment": "TraderVaultAI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        return mt5.order_send(request)

    def market_sell(
        self,
        symbol: str,
        volume: float,
        stop_loss: float,
        take_profit: float,
    ):

        tick = mt5.symbol_info_tick(symbol)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": tick.bid,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 20,
            "magic": 123456,
            "comment": "TraderVaultAI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        return mt5.order_send(request)