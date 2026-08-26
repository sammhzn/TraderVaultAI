from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATASET = Path("training_dataset.csv")

NUMERIC_FEATURES = [
    "entry",
    "stop_loss",
    "take_profit",
    "previous_day_high",
    "previous_day_low",
    "hour",

    # Original technical features
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


def profit_factor(df: pd.DataFrame) -> float:
    gross_profit = df.loc[df["profit"] > 0, "profit"].sum()
    gross_loss = abs(df.loc[df["profit"] < 0, "profit"].sum())

    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def build_model() -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def evaluate_period(
    test_df: pd.DataFrame,
    probabilities,
    threshold: float,
):
    selected = test_df[
        probabilities >= threshold
    ].copy()

    if selected.empty:
        return {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "profit": 0.0,
            "profit_factor": 0.0,
        }

    return {
        "trades": len(selected),
        "wins": int(
            (selected["result"] == "WIN").sum()
        ),
        "losses": int(
            (selected["result"] == "LOSS").sum()
        ),
        "win_rate": (
            selected["result"] == "WIN"
        ).mean(),
        "profit": selected["profit"].sum(),
        "profit_factor": profit_factor(selected),
    }


def main():

    if not DATASET.exists():
        raise FileNotFoundError(DATASET)

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

    df["target"] = (
        df["result"]
        .eq("WIN")
        .astype(int)
    )

    feature_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    # --------------------------------------------------
    # Walk-forward configuration
    #
    # Each fold trains only on the past and evaluates
    # on the immediately following future period.
    # --------------------------------------------------

    folds = [
        (0.50, 0.60),
        (0.60, 0.70),
        (0.70, 0.80),
        (0.80, 0.90),
        (0.90, 1.00),
    ]

    thresholds = [
        0.50,
        0.55,
        0.60,
    ]

    print("=" * 70)
    print("TRADERVAULTAI WALK-FORWARD VALIDATION")
    print("=" * 70)

    print(
        f"Total trades: {len(df)}"
    )

    print()

    all_results = []

    for fold_number, (train_start_pct, test_end_pct) in enumerate(
        folds,
        start=1,
    ):

        train_end = int(
            len(df) * train_start_pct
        )

        test_end = int(
            len(df) * test_end_pct
        )

        train_df = df.iloc[:train_end].copy()
        test_df = df.iloc[train_end:test_end].copy()

        if len(train_df) < 30 or len(test_df) < 5:
            continue

        X_train = train_df[feature_columns]
        y_train = train_df["target"]

        X_test = test_df[feature_columns]

        model = build_model()

        model.fit(
            X_train,
            y_train,
        )

        probabilities = model.predict_proba(
            X_test
        )[:, 1]

        baseline_pf = profit_factor(test_df)

        print("=" * 70)
        print(f"FOLD {fold_number}")
        print("=" * 70)

        print(
            f"Train: "
            f"{train_df.trade_date.min().date()} "
            f"to "
            f"{train_df.trade_date.max().date()} "
            f"({len(train_df)} trades)"
        )

        print(
            f"Test : "
            f"{test_df.trade_date.min().date()} "
            f"to "
            f"{test_df.trade_date.max().date()} "
            f"({len(test_df)} trades)"
        )

        print()
        print(
            f"Baseline profit: "
            f"{test_df.profit.sum():.2f}"
        )

        print(
            f"Baseline PF: "
            f"{baseline_pf:.2f}"
        )

        print()

        for threshold in thresholds:

            metrics = evaluate_period(
                test_df=test_df,
                probabilities=probabilities,
                threshold=threshold,
            )

            print(
                f"ML >= {threshold:.2f} | "
                f"Trades: {metrics['trades']:>3} | "
                f"Wins: {metrics['wins']:>3} | "
                f"Losses: {metrics['losses']:>3} | "
                f"Win rate: {metrics['win_rate']:.1%} | "
                f"Profit: {metrics['profit']:.2f} | "
                f"PF: {metrics['profit_factor']:.2f}"
            )

            all_results.append(
                {
                    "fold": fold_number,
                    "threshold": threshold,
                    **metrics,
                }
            )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    if not all_results:
        print("No valid folds.")
        return

    results_df = pd.DataFrame(
        all_results
    )

    print()
    print("=" * 70)
    print("WALK-FORWARD SUMMARY")
    print("=" * 70)

    summary = (
        results_df
        .groupby("threshold")
        .agg(
            folds=("fold", "count"),
            total_selected_trades=("trades", "sum"),
            total_wins=("wins", "sum"),
            total_losses=("losses", "sum"),
            total_profit=("profit", "sum"),
            average_profit=("profit", "mean"),
            average_pf=("profit_factor", "mean"),
        )
        .reset_index()
    )

    summary["win_rate"] = (
        summary["total_wins"]
        / summary["total_selected_trades"]
    )

    print(
        summary.to_string(
            index=False,
            float_format=lambda x: f"{x:.3f}",
        )
    )


if __name__ == "__main__":
    main()