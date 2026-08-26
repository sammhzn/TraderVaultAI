from dataclasses import dataclass


@dataclass
class RiskResult:
    lot_size: float
    risk_amount: float


class RiskManager:

    def calculate_position_size(
        self,
        balance: float,
        risk_percent: float,
        stop_loss_points: float,
        value_per_point: float = 1.0,
    ) -> RiskResult:

        risk_amount = balance * (risk_percent / 100)

        lot_size = risk_amount / (stop_loss_points * value_per_point)

        return RiskResult(
            lot_size=round(lot_size, 2),
            risk_amount=round(risk_amount, 2),
        )