from dataclasses import dataclass
from pathlib import Path

import MetaTrader5 as mt5
import pandas as pd

from app.backtesting.history_loader import HistoryLoader
from app.indicators.rsi import RSIIndicator


SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M5
BARS = 50000

RSI_PERIOD = 14

SWING_LEFT = 2
SWING_RIGHT = 2

MAX_DIVERGENCE_DISTANCE = 60

ZONE_ATR_MULTIPLIER = 0.50

RR = 4.0


@dataclass
class Trade:
    direction: str
    entry_time: object
    divergence_index: int
    first_pivot_index: int
    second_pivot_index: int
    entry: float
    stop_loss: float
    take_profit: float
    risk: float
    rsi_first: float
    rsi_second: float
    price_first: float
    price_second: float
    confirmation_index: int
    confirmation_open: float
    confirmation_close: float
    confirmation_high: float
    confirmation_low: float
    zone_distance_atr: float
    profit: float
    result: str


def is_swing_low(
    lows,
    index,
):
    start = index - SWING_LEFT
    end = index + SWING_RIGHT

    if start < 0 or end >= len(lows):
        return False

    current = lows[index]

    for i in range(start, end + 1):

        if i == index:
            continue

        if lows[i] <= current:
            return False

    return True


def is_swing_high(
    highs,
    index,
):
    start = index - SWING_LEFT
    end = index + SWING_RIGHT

    if start < 0 or end >= len(highs):
        return False

    current = highs[index]

    for i in range(start, end + 1):

        if i == index:
            continue

        if highs[i] >= current:
            return False

    return True


def calculate_atr(
    candles,
    period=14,
):
    tr_values = []

    previous_close = None

    for candle in candles:

        high = float(candle["high"])
        low = float(candle["low"])
        close = float(candle["close"])

        if previous_close is None:
            tr = high - low
        else:
            tr = max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )

        tr_values.append(tr)
        previous_close = close

    return (
        pd.Series(tr_values)
        .rolling(period)
        .mean()
        .tolist()
    )


def zone_near(
    price,
    swing_prices,
    atr_value,
):
    if atr_value is None or atr_value <= 0:
        return False

    tolerance = (
        atr_value
        * ZONE_ATR_MULTIPLIER
    )

    return any(
        abs(price - level)
        <= tolerance
        for level in swing_prices
    )


def calculate_trade_result(
    candles,
    entry_index,
    direction,
    entry,
    stop_loss,
    take_profit,
):
    for i in range(
        entry_index,
        len(candles),
    ):

        candle = candles[i]

        if direction == "BUY":

            stop_hit = (
                candle["low"]
                <= stop_loss
            )

            target_hit = (
                candle["high"]
                >= take_profit
            )

            # Conservative same-candle resolution:
            # SL first if both are touched.
            if stop_hit:
                return (
                    -abs(entry - stop_loss),
                    "LOSS",
                )

            if target_hit:
                return (
                    abs(take_profit - entry),
                    "WIN",
                )

        else:

            stop_hit = (
                candle["high"]
                >= stop_loss
            )

            target_hit = (
                candle["low"]
                <= take_profit
            )

            if stop_hit:
                return (
                    -abs(stop_loss - entry),
                    "LOSS",
                )

            if target_hit:
                return (
                    abs(entry - take_profit),
                    "WIN",
                )

    return (
        0.0,
        "OPEN",
    )


def main():

    print("=" * 80)
    print(
        "TRADERVAULTAI "
        "RSI DIVERGENCE M5 BACKTEST"
    )
    print("=" * 80)

    loader = HistoryLoader()

    candles = loader.load(
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        bars=BARS,
    )

    print(
        f"Candles loaded : {len(candles)}"
    )

    if not candles:
        print(
            "No candles loaded."
        )
        return

    rsi_indicator = RSIIndicator()

    rsi = rsi_indicator.calculate(
        candles,
        period=RSI_PERIOD,
    )

    atr = calculate_atr(
        candles,
        period=RSI_PERIOD,
    )

    highs = [
        float(c["high"])
        for c in candles
    ]

    lows = [
        float(c["low"])
        for c in candles
    ]

    # Confirmed pivots.
    swing_lows = []
    swing_highs = []

    for i in range(
        SWING_LEFT,
        len(candles) - SWING_RIGHT,
    ):

        if is_swing_low(
            lows,
            i,
        ):
            swing_lows.append(i)

        if is_swing_high(
            highs,
            i,
        ):
            swing_highs.append(i)

    trades = []

    used_divergence_indices = set()

    # --------------------------------------------------
    # Scan divergence pivots
    # --------------------------------------------------

    for second_index in range(
        SWING_LEFT + SWING_RIGHT,
        len(candles) - 2,
    ):

        # ----------------------------------------------
        # Bullish divergence
        # ----------------------------------------------

        if (
            second_index
            in swing_lows
        ):

            previous_lows = [
                i
                for i in swing_lows
                if (
                    i < second_index
                    and second_index - i
                    <= MAX_DIVERGENCE_DISTANCE
                )
            ]

            if previous_lows:

                first_index = (
                    previous_lows[-1]
                )

                price_first = lows[
                    first_index
                ]

                price_second = lows[
                    second_index
                ]

                rsi_first = rsi[
                    first_index
                ]

                rsi_second = rsi[
                    second_index
                ]

                bullish_divergence = (
                    price_second
                    < price_first
                    and rsi_second
                    > rsi_first
                )

                if bullish_divergence:

                    atr_value = atr[
                        second_index
                    ]

                    support_levels = [
                        lows[i]
                        for i in swing_lows
                        if i < second_index
                    ]

                    valid_zone = zone_near(
                        price_second,
                        support_levels,
                        atr_value,
                    )

                    if valid_zone:

                        if second_index in used_divergence_indices:
                            continue

                        used_divergence_indices.add(
                            second_index
                        )

                        # ----------------------------------
                        # Confirmation candle
                        # ----------------------------------

                        confirmation_index = (
                            second_index
                            + SWING_RIGHT
                            + 1
                        )

                        if (
                            confirmation_index
                            >= len(candles)
                        ):
                            continue

                        confirmation = candles[
                            confirmation_index
                        ]

                        bullish_confirmation = (
                            confirmation["close"]
                            > confirmation["open"]
                        )

                        if not bullish_confirmation:
                            continue

                        entry_trigger = (
                            float(
                                confirmation["high"]
                            )
                        )

                        # ----------------------------------
                        # Find breakout
                        # ----------------------------------

                        entry_index = None

                        for j in range(
                            confirmation_index + 1,
                            min(
                                confirmation_index + 20,
                                len(candles),
                            ),
                        ):

                            if (
                                candles[j]["high"]
                                > entry_trigger
                            ):

                                entry_index = j
                                break

                        if entry_index is None:
                            continue

                        entry = entry_trigger

                        stop_loss = (
                            price_second
                        )

                        risk = (
                            entry
                            - stop_loss
                        )

                        if risk <= 0:
                            continue

                        take_profit = (
                            entry
                            + risk * RR
                        )

                        profit, result = (
                            calculate_trade_result(
                                candles,
                                entry_index,
                                "BUY",
                                entry,
                                stop_loss,
                                take_profit,
                            )
                        )

                        if result != "OPEN":
                            zone_distance_atr = (
                                min(
                                    abs(price_second - level)
                                    for level in support_levels
                                )
                                / atr_value
                                if support_levels and atr_value
                                else None
                            )

                            trades.append(
                                Trade(
                                    direction="BUY",
                                    entry_time=candles[entry_index]["time"],
                                    divergence_index=second_index,
                                    first_pivot_index=first_index,
                                    second_pivot_index=second_index,
                                    entry=entry,
                                    stop_loss=stop_loss,
                                    take_profit=take_profit,
                                    risk=risk,
                                    rsi_first=float(rsi_first),
                                    rsi_second=float(rsi_second),
                                    price_first=price_first,
                                    price_second=price_second,
                                    confirmation_index=confirmation_index,
                                    confirmation_open=float(confirmation["open"]),
                                    confirmation_close=float(confirmation["close"]),
                                    confirmation_high=float(confirmation["high"]),
                                    confirmation_low=float(confirmation["low"]),
                                    zone_distance_atr=zone_distance_atr,
                                    profit=profit,
                                    result=result,
                                )
                            )

        # ----------------------------------------------
        # Bearish divergence
        # ----------------------------------------------

        if (
            second_index
            in swing_highs
        ):

            previous_highs = [
                i
                for i in swing_highs
                if (
                    i < second_index
                    and second_index - i
                    <= MAX_DIVERGENCE_DISTANCE
                )
            ]

            if previous_highs:

                first_index = (
                    previous_highs[-1]
                )

                price_first = highs[
                    first_index
                ]

                price_second = highs[
                    second_index
                ]

                rsi_first = rsi[
                    first_index
                ]

                rsi_second = rsi[
                    second_index
                ]

                bearish_divergence = (
                    price_second
                    > price_first
                    and rsi_second
                    < rsi_first
                )

                if bearish_divergence:

                    atr_value = atr[
                        second_index
                    ]

                    resistance_levels = [
                        highs[i]
                        for i in swing_highs
                        if i < second_index
                    ]

                    valid_zone = zone_near(
                        price_second,
                        resistance_levels,
                        atr_value,
                    )

                    if valid_zone:

                        if second_index in used_divergence_indices:
                            continue

                        used_divergence_indices.add(
                            second_index
                        )

                        confirmation_index = (
                            second_index
                            + SWING_RIGHT
                            + 1
                        )

                        if (
                            confirmation_index
                            >= len(candles)
                        ):
                            continue

                        confirmation = candles[
                            confirmation_index
                        ]

                        bearish_confirmation = (
                            confirmation["close"]
                            < confirmation["open"]
                        )

                        if not bearish_confirmation:
                            continue

                        entry_trigger = (
                            float(
                                confirmation["low"]
                            )
                        )

                        entry_index = None

                        for j in range(
                            confirmation_index + 1,
                            min(
                                confirmation_index + 20,
                                len(candles),
                            ),
                        ):

                            if (
                                candles[j]["low"]
                                < entry_trigger
                            ):

                                entry_index = j
                                break

                        if entry_index is None:
                            continue

                        entry = entry_trigger

                        stop_loss = (
                            price_second
                        )

                        risk = (
                            stop_loss
                            - entry
                        )

                        if risk <= 0:
                            continue

                        take_profit = (
                            entry
                            - risk * RR
                        )

                        profit, result = (
                            calculate_trade_result(
                                candles,
                                entry_index,
                                "SELL",
                                entry,
                                stop_loss,
                                take_profit,
                            )
                        )

                        if result != "OPEN":
                            zone_distance_atr = (
                                min(
                                    abs(price_second - level)
                                    for level in resistance_levels
                                )
                                / atr_value
                                if resistance_levels and atr_value
                                else None
                            )

                            trades.append(
                                Trade(
                                    direction="SELL",
                                    entry_time=candles[entry_index]["time"],
                                    divergence_index=second_index,
                                    first_pivot_index=first_index,
                                    second_pivot_index=second_index,
                                    entry=entry,
                                    stop_loss=stop_loss,
                                    take_profit=take_profit,
                                    risk=risk,
                                    rsi_first=float(rsi_first),
                                    rsi_second=float(rsi_second),
                                    price_first=price_first,
                                    price_second=price_second,
                                    confirmation_index=confirmation_index,
                                    confirmation_open=float(confirmation["open"]),
                                    confirmation_close=float(confirmation["close"]),
                                    confirmation_high=float(confirmation["high"]),
                                    confirmation_low=float(confirmation["low"]),
                                    zone_distance_atr=zone_distance_atr,
                                    profit=profit,
                                    result=result,
                                )
                            )
    # --------------------------------------------------
    # Export trades for analysis
    # --------------------------------------------------

    trade_rows = [
        {
            "direction": trade.direction,
            "entry_time": trade.entry_time,
            "divergence_index": trade.divergence_index,
            "first_pivot_index": trade.first_pivot_index,
            "second_pivot_index": trade.second_pivot_index,
            "entry": trade.entry,
            "stop_loss": trade.stop_loss,
            "take_profit": trade.take_profit,
            "risk": trade.risk,
            "rsi_first": trade.rsi_first,
            "rsi_second": trade.rsi_second,
            "price_first": trade.price_first,
            "price_second": trade.price_second,
            "confirmation_index": trade.confirmation_index,
            "confirmation_open": trade.confirmation_open,
            "confirmation_close": trade.confirmation_close,
            "confirmation_high": trade.confirmation_high,
            "confirmation_low": trade.confirmation_low,
            "zone_distance_atr": trade.zone_distance_atr,
            "profit": trade.profit,
            "result": trade.result,
        }
        for trade in trades
    ]

    output = Path(
        "rsi_divergence_trades.csv"
    )

    pd.DataFrame(
        trade_rows
    ).to_csv(
        output,
        index=False,
    )

    print(
        f"Trades exported  : {output}"
    )
    
    # --------------------------------------------------
    # Report
    # --------------------------------------------------

    total_trades = len(trades)

    wins = sum(
        1
        for trade in trades
        if trade.result == "WIN"
    )

    losses = sum(
        1
        for trade in trades
        if trade.result == "LOSS"
    )

    gross_profit = sum(
        trade.profit
        for trade in trades
        if trade.profit > 0
    )

    gross_loss = abs(
        sum(
            trade.profit
            for trade in trades
            if trade.profit < 0
        )
    )

    net_profit = sum(
        trade.profit
        for trade in trades
    )

    win_rate = (
        wins / total_trades
        if total_trades
        else 0.0
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss
        else float("inf")
    )

    print()
    print("=" * 80)
    print(
        "RSI DIVERGENCE RESULTS"
    )
    print("=" * 80)

    print(
        f"Trades         : {total_trades}"
    )

    print(
        f"Wins           : {wins}"
    )

    print(
        f"Losses         : {losses}"
    )

    print(
        f"Win rate       : {win_rate:.2%}"
    )

    print(
        f"Gross profit   : {gross_profit:.2f}"
    )

    print(
        f"Gross loss     : {gross_loss:.2f}"
    )

    print(
        f"Net profit     : {net_profit:.2f}"
    )

    print(
        f"Profit factor  : {profit_factor:.2f}"
    )

    print()

    buy_trades = [
        t for t in trades
        if t.direction == "BUY"
    ]

    sell_trades = [
        t for t in trades
        if t.direction == "SELL"
    ]

    print(
        f"BUY trades     : {len(buy_trades)}"
    )

    print(
        f"SELL trades    : {len(sell_trades)}"
    )

    print()

    print(
        "First 20 trades:"
    )

    for trade in trades[:20]:

        print(
            f"{trade.direction:<4} "
            f"entry={trade.entry:.2f} "
            f"SL={trade.stop_loss:.2f} "
            f"TP={trade.take_profit:.2f} "
            f"profit={trade.profit:.2f} "
            f"{trade.result}"
        )


if __name__ == "__main__":
    main()