from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TradeSetup:

    id: str

    created_at: datetime

    direction: str

    state: str

    sweep_level: str

    entry_price: Optional[float] = None

    stop_loss: Optional[float] = None

    tp1: Optional[float] = None

    tp2: Optional[float] = None

    layers: int = 1

    reason: str = ""