class CandleExecutor:

    def process_candle(self, candle, trades):

        closed = 0

        for trade in trades.active_trades():

            # BUY
            if trade.direction == "BUY":

                if candle["low"] <= trade.stop_loss:
                    trade.active = False
                    closed += 1
                    continue

                if candle["high"] >= trade.take_profit:
                    trade.active = False
                    closed += 1
                    continue

            # SELL
            if trade.direction == "SELL":

                if candle["high"] >= trade.stop_loss:
                    trade.active = False
                    closed += 1
                    continue

                if candle["low"] <= trade.take_profit:
                    trade.active = False
                    closed += 1
                    continue

        return closed