from pathlib import Path

import pandas as pd


DATASET = Path("training_dataset.csv")

FEATURES = [
    "rsi",
    "atr",
    "adx",
    "macd_histogram_atr",
    "bollinger_width_atr",
    "ema_spread_atr",
    "di_spread",
    "entry_distance_from_pdh_atr",
    "entry_distance_from_pdl_atr",
]


def main():

    if not DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

    df = pd.read_csv(DATASET)

    df["trade_date"] = pd.to_datetime(
        df["trade_date"],
        errors="coerce",
    )

    df = (
        df.dropna(subset=["trade_date"])
        .sort_values(["trade_date", "hour"])
        .reset_index(drop=True)
    )

    # Five chronological periods.
    df["period"] = pd.qcut(
        df["trade_date"].rank(method="first"),
        5,
        labels=[
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
        ],
    )

    print("=" * 75)
    print("TRADERVAULTAI FEATURE DRIFT ANALYSIS")
    print("=" * 75)

    print(
        f"Trades : {len(df)}"
    )

    print(
        f"Dates  : "
        f"{df.trade_date.min().date()} "
        f"to "
        f"{df.trade_date.max().date()}"
    )

    # --------------------------------------------------
    # Feature means by period
    # --------------------------------------------------

    print()
    print("=" * 75)
    print("FEATURE MEANS BY PERIOD")
    print("=" * 75)

    means = (
        df.groupby("period", observed=True)[FEATURES]
        .mean()
        .round(3)
    )

    print(
        means.to_string()
    )

    # --------------------------------------------------
    # Feature standard deviations
    # --------------------------------------------------

    print()
    print("=" * 75)
    print("FEATURE STANDARD DEVIATIONS BY PERIOD")
    print("=" * 75)

    std = (
        df.groupby("period", observed=True)[FEATURES]
        .std()
        .round(3)
    )

    print(
        std.to_string()
    )

    # --------------------------------------------------
    # Win rate by period
    # --------------------------------------------------

    print()
    print("=" * 75)
    print("PERIOD PERFORMANCE")
    print("=" * 75)

    performance = (
        df.groupby("period", observed=True)
        .agg(
            trades=("result", "size"),
            wins=(
                "result",
                lambda x: (x == "WIN").sum(),
            ),
            losses=(
                "result",
                lambda x: (x == "LOSS").sum(),
            ),
            profit=("profit", "sum"),
        )
    )

    performance["win_rate"] = (
        performance["wins"]
        / performance["trades"]
    )

    print(
        performance.round(3).to_string()
    )

    # --------------------------------------------------
    # Market regime distribution
    # --------------------------------------------------

    print()
    print("=" * 75)
    print("MARKET REGIME DISTRIBUTION")
    print("=" * 75)

    regime = pd.crosstab(
        df["period"],
        df["market_regime"],
        normalize="index",
    ) * 100

    print(
        regime.round(1).to_string()
    )

    # --------------------------------------------------
    # Direction distribution
    # --------------------------------------------------

    print()
    print("=" * 75)
    print("DIRECTION DISTRIBUTION")
    print("=" * 75)

    direction = pd.crosstab(
        df["period"],
        df["direction"],
        normalize="index",
    ) * 100

    print(
        direction.round(1).to_string()
    )

    # --------------------------------------------------
    # Winners vs losses by period
    # --------------------------------------------------

    print()
    print("=" * 75)
    print("WIN/LOSS MIX BY PERIOD")
    print("=" * 75)

    win_loss = (
        df.groupby(
            ["period", "result"],
            observed=True,
        )
        .agg(
            trades=("result", "size"),
            profit=("profit", "sum"),
        )
    )

    print(
        win_loss.round(3).to_string()
    )


if __name__ == "__main__":
    main()