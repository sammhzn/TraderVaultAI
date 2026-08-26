from dataclasses import dataclass


@dataclass
class ManagedPosition:
    ticket: int
    layer: int
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    break_even: bool = False
    active: bool = True


class PositionManager:

    def __init__(self):
        self.positions = []

    def add(self, position: ManagedPosition):
        self.positions.append(position)

    def active_positions(self):
        return [p for p in self.positions if p.active]

    def count(self):
        return len(self.active_positions())

    def newest(self):
        active = self.active_positions()

        if not active:
            return None

        return max(active, key=lambda p: p.layer)