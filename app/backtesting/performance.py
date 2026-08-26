from dataclasses import dataclass


@dataclass
class PerformanceReport:
    total_trades: int
    wins: int
    losses: int

    gross_profit: float
    gross_loss: float
    net_profit: float
    profit_factor: float

    average_win: float
    average_loss: float

    @property
    def win_rate(self):

        if self.total_trades == 0:
            return 0.0

        return round(
            (self.wins / self.total_trades) * 100,
            2,
        )


class PerformanceAnalyzer:
    def analyze(
            self,
            wins: int,
            losses: int,
            gross_profit: float,
            gross_loss: float,
            net_profit: float,
            profit_factor: float,
    ):

        average_win = 0.0

        if wins > 0:
            average_win = round(
                gross_profit / wins,
                2,
            )

        average_loss = 0.0

        if losses > 0:
            average_loss = round(
                gross_loss / losses,
                2,
            )

        return PerformanceReport(
            total_trades=wins + losses,
            wins=wins,
            losses=losses,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            net_profit=net_profit,
            profit_factor=profit_factor,
            average_win=average_win,
            average_loss=average_loss,
        )

        return PerformanceReport(
            total_trades=wins + losses,
            wins=wins,
            losses=losses,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            net_profit=net_profit,
            profit_factor=profit_factor,
        )