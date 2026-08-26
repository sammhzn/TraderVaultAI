from pathlib import Path

import pandas as pd
import joblib


DATASET = Path("training_dataset.csv")
MODEL_PATH = Path("app/ai/trade_filter_model.joblib")

NUMERIC_FEATURES = [
    "entry",
    "stop_loss",
    "take_profit",
    "previous_day_high",
    "previous_day_low",
    "hour",
    "ema20",
    "ema50",
    "rsi",
    "atr",
    "macd",
    "macd_signal",
    "macd_histogram",
    "adx",
    "plus_di",
    "minus_di",
    "bollinger_middle",
    "bollinger_upper",
    "bollinger_lower",
    "bollinger_width",

    # Normalized features
    "entry_distance_from_pdh_atr",
    "entry_distance_from_pdl_atr",
    "ema_spread",
    "ema_spread_atr",
    "risk_distance",
    "reward_distance",
    "risk_atr",
    "reward_atr",
    "macd_histogram_atr",
    "bollinger_width_atr",
    "bollinger_position",
    "di_spread",
]

CATEGORICAL_FEATURES = [
    "direction",
    "day",
    "market_regime",
    "trend",
    "trend_strength",
    "momentum",
    "directional_bias",
]


def profit_factor(df):
    gross_profit = df.loc[df["profit"] > 0, "profit"].sum()
    gross_loss = abs(df.loc[df["profit"] < 0, "profit"].sum())

    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def max_drawdown(profits):
    equity = profits.cumsum()
    peak = equity.cummax()
    drawdown = equity - peak
    return abs(drawdown.min())


def metrics(df):
    if df.empty:
        return {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "profit": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "avg_profit": 0.0,
        }

    wins = int((df["result"] == "WIN").sum())
    losses = int((df["result"] == "LOSS").sum())

    return {
        "trades": len(df),
        "wins": wins,
        "losses": losses,
        "win_rate": wins / len(df),
        "profit": df["profit"].sum(),
        "profit_factor": profit_factor(df),
        "max_drawdown": max_drawdown(df["profit"]),
        "avg_profit": df["profit"].mean(),
    }

def main():

    if not DATASET.exists():
        raise FileNotFoundError(DATASET)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(MODEL_PATH)

    df = pd.read_csv(DATASET)

    df["trade_date"] = pd.to_datetime(
        df["trade_date"],
        errors="coerce",
    )

    df = (
        df.dropna(
            subset=["trade_date", "result"]
        )
        .sort_values(
            ["trade_date", "hour"]
        )
        .reset_index(drop=True)
    )

    split_index = int(len(df) * 0.70)

    test_df = df.iloc[split_index:].copy()

    feature_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    X_test = test_df[feature_columns]

    model = joblib.load(MODEL_PATH)

    test_df["win_probability"] = model.predict_proba(
        X_test
    )[:, 1]

    thresholds = [
        0.00,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
    ]

    print("=" * 75)
    print("TRADERVAULTAI PROFITABILITY EVALUATION")
    print("=" * 75)

    print(
        f"Test period: "
        f"{test_df.trade_date.min().date()} "
        f"to "
        f"{test_df.trade_date.max().date()}"
    )

    print(f"Test trades: {len(test_df)}")
    print()

    print(
        f"{'Threshold':>10} "
        f"{'Trades':>8} "
        f"{'Wins':>6} "
        f"{'Losses':>8} "
        f"{'Win%':>8} "
        f"{'Profit':>10} "
        f"{'PF':>8} "
        f"{'MaxDD':>10} "
        f"{'Avg':>9}"
    )

    print("-" * 90)

    for threshold in thresholds:

        if threshold == 0:
            selected = test_df.copy()
        else:
            selected = test_df[
                test_df["win_probability"] >= threshold
            ].copy()

        m = metrics(selected)

        pf = (
            f"{m['profit_factor']:.2f}"
            if m["profit_factor"] != float("inf")
            else "INF"
        )

        print(
            f"{threshold:>10.2f} "
            f"{m['trades']:>8} "
            f"{m['wins']:>6} "
            f"{m['losses']:>8} "
            f"{m['win_rate']:>7.1%} "
            f"{m['profit']:>10.2f} "
            f"{pf:>8} "
            f"{m['max_drawdown']:>10.2f} "
            f"{m['avg_profit']:>9.2f}"
        )

    print()
    print("=" * 75)
    print("OUT-OF-SAMPLE EQUITY BY THRESHOLD")
    print("=" * 75)

    for threshold in [0.50, 0.55, 0.60]:

        selected = test_df[
            test_df["win_probability"] >= threshold
        ].copy()

        if selected.empty:
            continue

        selected = selected.sort_values(
            ["trade_date", "hour"]
        )

        selected["equity"] = selected[
            "profit"
        ].cumsum()

        print(
            f"\nThreshold {threshold:.2f}:"
        )

        print(
            selected[
                [
                    "trade_date",
                    "direction",
                    "win_probability",
                    "profit",
                    "equity",
                    "result",
                ]
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()