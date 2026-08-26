import MetaTrader5 as mt5


class MT5Connector:

    def connect(self):

        if mt5.initialize():
            return True

        return False

    def disconnect(self):

        mt5.shutdown()