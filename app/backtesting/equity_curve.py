from dataclasses import dataclass


@dataclass
class EquityPoint:
    trade_number: int
    balance: float


class EquityCurve:

    def __init__(self, starting_balance=10000):
        self.balance = starting_balance
        self.points = [
            EquityPoint(0, starting_balance)
        ]

    def record_trade(self, profit):

        self.balance += profit

        self.points.append(
            EquityPoint(
                trade_number=len(self.points),
                balance=round(self.balance, 2),
            )
        )

    def latest_balance(self):
        return self.balance