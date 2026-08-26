class EquityCurve:

    def build(self, trades):

        equity = []

        balance = 0.0

        for trade in trades:

            balance += trade.profit

            equity.append(balance)

        return equity