from pathlib import Path

import joblib
import pandas as pd


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
    gross_profit = df.loc[df.profit > 0, "profit"].sum()
    gross_loss = abs(df.loc[df.profit < 0, "profit"].sum())

    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


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
        df.dropna(subset=["trade_date", "result"])
        .sort_values(["trade_date", "hour"])
        .reset_index(drop=True)
    )

    split_index = int(len(df) * 0.70)

    test_df = df.iloc[split_index:].copy()

    X_test = test_df[
        NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ]

    model = joblib.load(MODEL_PATH)

    test_df["win_probability"] = model.predict_proba(
        X_test
    )[:, 1]

    print("=" * 60)
    print("TRADEVaultAI ML TRADE-FILTER EVALUATION")
    print("=" * 60)

    print(
        f"Test period: "
        f"{test_df.trade_date.min().date()} "
        f"to "
        f"{test_df.trade_date.max().date()}"
    )

    print(f"Test trades: {len(test_df)}")
    print()

    baseline_pf = profit_factor(test_df)

    print("BASELINE")
    print(f"Trades        : {len(test_df)}")
    print(
        f"Wins          : "
        f"{(test_df.result == 'WIN').sum()}"
    )
    print(
        f"Losses        : "
        f"{(test_df.result == 'LOSS').sum()}"
    )
    print(
        f"Win rate      : "
        f"{(test_df.result == 'WIN').mean():.2%}"
    )
    print(
        f"Profit        : "
        f"{test_df.profit.sum():.2f}"
    )
    print(
        f"Profit factor : "
        f"{baseline_pf:.2f}"
    )

    print()
    print("=" * 60)
    print("MODEL FILTER")
    print("=" * 60)

    thresholds = [
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
    ]

    for threshold in thresholds:

        filtered = test_df[
            test_df.win_probability >= threshold
        ]

        if filtered.empty:
            print()
            print(f"Threshold >= {threshold:.2f}")
            print("No trades selected")
            continue

        pf = profit_factor(filtered)

        print()
        print(f"Threshold >= {threshold:.2f}")
        print(f"Trades        : {len(filtered)}")
        print(
            f"Wins          : "
            f"{(filtered.result == 'WIN').sum()}"
        )
        print(
            f"Losses        : "
            f"{(filtered.result == 'LOSS').sum()}"
        )
        print(
            f"Win rate      : "
            f"{(filtered.result == 'WIN').mean():.2%}"
        )
        print(
            f"Profit        : "
            f"{filtered.profit.sum():.2f}"
        )
        print(
            f"Profit factor : "
            f"{pf:.2f}"
        )

    print()
    print("=" * 60)
    print("HIGHEST-PROBABILITY TRADES")
    print("=" * 60)

    print(
        test_df[
            [
                "trade_date",
                "direction",
                "win_probability",
                "profit",
                "result",
            ]
        ]
        .sort_values(
            "win_probability",
            ascending=False,
        )
        .head(15)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()