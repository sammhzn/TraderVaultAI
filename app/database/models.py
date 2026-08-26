from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import DateTime

from app.database.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    symbol = Column(
        String,
        nullable=False,
    )

    timeframe = Column(
        String,
        nullable=False,
    )

    strategy = Column(
        String,
        nullable=False,
    )

    direction = Column(
        String,
        nullable=False,
    )

    entry = Column(
        Float,
        nullable=False,
    )

    stop_loss = Column(
        Float,
        nullable=False,
    )

    take_profit = Column(
        Float,
        nullable=False,
    )

    layer = Column(
        Integer,
        default=1,
    )

    open_time = Column(
        DateTime,
    )

    close_time = Column(
        DateTime,
    )

    result = Column(
        String,
        default="OPEN",
    )

    profit = Column(
        Float,
        default=0.0,
    )