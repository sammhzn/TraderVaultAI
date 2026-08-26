from dataclasses import dataclass


@dataclass
class Position:
    layer: int
    direction: str
    entry: float
    stop_loss: float
    active: bool = True


class TradeManager:

    def __init__(self):
        self.positions = []

    def open_trade(
        self,
        direction,
        entry,
        stop_loss,
        layer=1,
    ):

        position = Position(
            layer=layer,
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
        )

        self.positions.append(position)

        return position

    def active_positions(self):

        return [p for p in self.positions if p.active]

    def close_tp1(self):

        active = self.active_positions()

        if len(active) <= 1:
            return active

        newest = sorted(
            active,
            key=lambda x: x.layer,
            reverse=True,
        )

        newest[0].active = False

        for p in newest[1:]:
            p.stop_loss = p.entry

        return self.active_positions()