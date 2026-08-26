from pathlib import Path
from datetime import datetime

import pandas as pd

from app.backtesting.history_loader import HistoryLoader


DATASET = Path("training_dataset.csv")

SYMBOL = "XAUUSD"
BARS = 250000

R_LEVELS = [
    0.25,
    0.50,
    0.75,
    1.00,
    1.50,
    2.00,
]


def load_trades():
    if not DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

    df = pd.read_csv(DATASET)

    required = [
        "direction",
        "entry",
        "stop_loss",
        "take_profit",
        "trade_date",
        "profit",
        "result",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    df["trade_date"] = pd.to_datetime(
        df["trade_date"],
        errors="coerce",
    )

    return (
        df.dropna(
            subset=[
                "trade_date",
                "entry",
                "stop_loss",
                "take_profit",
            ]
        )
        .sort_values(
            ["trade_date", "hour"]
            if "hour" in df.columns
            else ["trade_date"]
        )
        .reset_index(drop=True)
    )


def candle_time(candle):
    return datetime.fromtimestamp(
        candle["time"]
    )


def calculate_excursion(
    trade,
    candles,
):
    entry = float(trade["entry"])
    stop_loss = float(trade["stop_loss"])
    take_profit = float(trade["take_profit"])

    direction = trade["direction"]

    open_time = trade["trade_date"]

    # The CSV only contains the trade date, so use the
    # hour when available and otherwise skip precise
    # intraday excursion measurement.
    if "hour" in trade.index and pd.notna(trade["hour"]):
        hour = int(trade["hour"])

        # Start at the beginning of the recorded hour.
        trade_start = open_time.replace(
            hour=hour,
            minute=0,
            second=0,
            microsecond=0,
        )
    else:
        trade_start = open_time

    # Risk in price units.
    risk = abs(
        entry - stop_loss
    )

    if risk <= 0:
        return None

    mae_price = 0.0
    mfe_price = 0.0

    hit_stop = False
    hit_target = False

    first_exit_time = None

    for candle in candles:

        time = candle_time(candle)

        if time < trade_start:
            continue

        if direction == "BUY":

            favorable = (
                candle["high"] - entry
            )

            adverse = (
                entry - candle["low"]
            )

            if favorable > mfe_price:
                mfe_price = favorable

            if adverse > mae_price:
                mae_price = adverse

            if candle["low"] <= stop_loss:
                hit_stop = True
                first_exit_time = time
                break

            if candle["high"] >= take_profit:
                hit_target = True
                first_exit_time = time
                break

        else:

            favorable = (
                entry - candle["low"]
            )

            adverse = (
                candle["high"] - entry
            )

            if favorable > mfe_price:
                mfe_price = favorable

            if adverse > mae_price:
                mae_price = adverse

            if candle["high"] >= stop_loss:
                hit_stop = True
                first_exit_time = time
                break

            if candle["low"] <= take_profit:
                hit_target = True
                first_exit_time = time
                break

    mae_r = mae_price / risk
    mfe_r = mfe_price / risk

    return {
        "mae_price": mae_price,
        "mfe_price": mfe_price,
        "mae_r": mae_r,
        "mfe_r": mfe_r,
        "hit_stop_first": hit_stop,
        "hit_target_first": hit_target,
        "first_exit_time": first_exit_time,
    }


def threshold_reached(
    mfe_r,
    threshold,
):
    return mfe_r >= threshold


def main():

    trades = load_trades()

    print("=" * 80)
    print("TRADERVAULTAI MAE / MFE ANALYSIS")
    print("=" * 80)

    print(
        f"Trades: {len(trades)}"
    )

    print()

    loader = HistoryLoader()

    candles = loader.load(
        symbol=SYMBOL,
        bars=BARS,
    )

    print(
        f"Historical candles loaded: "
        f"{len(candles)}"
    )

    excursion_rows = []

    for index, trade in trades.iterrows():

        excursion = calculate_excursion(
            trade,
            candles,
        )

        if excursion is None:
            continue

        row = trade.to_dict()

        row.update(excursion)

        excursion_rows.append(row)

    if not excursion_rows:
        print(
            "No excursion data could be calculated."
        )
        return

    result = pd.DataFrame(
        excursion_rows
    )

    # --------------------------------------------------
    # Overall excursion statistics
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("OVERALL MAE / MFE")
    print("=" * 80)

    print(
        result[
            [
                "mae_r",
                "mfe_r",
            ]
        ]
        .describe()
        .round(3)
        .to_string()
    )

    # --------------------------------------------------
    # Winners vs losers
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("WINNERS VS LOSERS")
    print("=" * 80)

    grouped = (
        result.groupby("result")[
            [
                "mae_r",
                "mfe_r",
            ]
        ]
        .agg(
            [
                "count",
                "mean",
                "median",
                "max",
            ]
        )
        .round(3)
    )

    print(
        grouped.to_string()
    )

    # --------------------------------------------------
    # MAE / MFE by direction
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("MAE / MFE BY DIRECTION")
    print("=" * 80)

    direction_stats = (
        result.groupby("direction")[
            [
                "mae_r",
                "mfe_r",
            ]
        ]
        .mean()
        .round(3)
    )

    print(
        direction_stats.to_string()
    )

    # --------------------------------------------------
    # How many trades reach each R level?
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("MFE THRESHOLDS")
    print("=" * 80)

    total = len(result)

    for r_level in R_LEVELS:

        reached = (
            result["mfe_r"]
            >= r_level
        ).sum()

        percentage = (
            reached / total
            if total
            else 0.0
        )

        print(
            f"+{r_level:.2f}R : "
            f"{reached:>3}/{total} "
            f"({percentage:.1%})"
        )

    # --------------------------------------------------
    # Losing trades that reached profit first
    # --------------------------------------------------

    losses = result[
        result["result"] == "LOSS"
    ].copy()

    print()
    print("=" * 80)
    print("LOSING TRADES THAT REACHED PROFIT")
    print("=" * 80)

    if losses.empty:

        print("No losing trades.")

    else:

        for r_level in [
            0.25,
            0.50,
            0.75,
            1.00,
        ]:

            reached = (
                losses["mfe_r"]
                >= r_level
            ).sum()

            percentage = (
                reached / len(losses)
            )

            print(
                f"Losses reaching "
                f"+{r_level:.2f}R: "
                f"{reached}/{len(losses)} "
                f"({percentage:.1%})"
            )

    # --------------------------------------------------
    # Winners that suffered adverse movement
    # --------------------------------------------------

    winners = result[
        result["result"] == "WIN"
    ].copy()

    print()
    print("=" * 80)
    print("WINNER ADVERSE EXCURSION")
    print("=" * 80)

    if winners.empty:

        print("No winning trades.")

    else:

        for r_level in [
            0.25,
            0.50,
            0.75,
            1.00,
        ]:

            count = (
                winners["mae_r"]
                >= r_level
            ).sum()

            percentage = (
                count / len(winners)
            )

            print(
                f"Winners reaching "
                f"-{r_level:.2f}R adverse: "
                f"{count}/{len(winners)} "
                f"({percentage:.1%})"
            )

    # --------------------------------------------------
    # Save analysis
    # --------------------------------------------------

    output = Path(
        "trade_excursion_analysis.csv"
    )

    result.to_csv(
        output,
        index=False,
    )

    print()
    print("=" * 80)
    print(
        f"Saved: {output}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()