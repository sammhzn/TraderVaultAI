from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATASET = Path("training_dataset.csv")

TRAIN_WINDOW = 60
VALIDATION_WINDOW = 20
TEST_WINDOW = 15

PERCENTILES = [0.10, 0.20, 0.30, 0.40]


NUMERIC_FEATURES = [
    "hour",
    "rsi",
    "atr",
    "adx",
    "plus_di",
    "minus_di",
    "macd_histogram",
    "bollinger_width",
    "entry_distance_from_pdh_atr",
    "entry_distance_from_pdl_atr",
    "ema_spread_atr",
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


def load_dataset():
    if not DATASET.exists():
        raise FileNotFoundError(DATASET)

    df = pd.read_csv(DATASET)

    df["trade_date"] = pd.to_datetime(
        df["trade_date"],
        errors="coerce",
    )

    required = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
        + ["trade_date", "result", "profit"]
    )

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = (
        df.dropna(
            subset=["trade_date", "result", "profit"]
        )
        .sort_values(["trade_date", "hour"])
        .reset_index(drop=True)
    )

    df["target"] = (
        df["result"]
        .eq("WIN")
        .astype(int)
    )

    return df


def build_model():
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
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


def profit_factor(df):
    if df.empty:
        return 0.0

    gross_profit = df.loc[
        df["profit"] > 0,
        "profit",
    ].sum()

    gross_loss = abs(
        df.loc[
            df["profit"] < 0,
            "profit",
        ].sum()
    )

    if gross_loss == 0:
        return (
            float("inf")
            if gross_profit > 0
            else 0.0
        )

    return gross_profit / gross_loss


def max_drawdown(df):
    if df.empty:
        return 0.0

    ordered = df.sort_values(
        ["trade_date", "hour"]
    )

    equity = ordered["profit"].cumsum()
    peak = equity.cummax()

    return abs((equity - peak).min())


def evaluate_percentile(
    df,
    probabilities,
    percentile,
):
    scored = df.copy()

    scored["model_score"] = pd.Series(
        probabilities,
        index=scored.index,
        dtype="float64",
    )

    # Higher score = higher confidence.
    scored = scored.sort_values(
        "model_score",
        ascending=False,
    )

    count = max(
        1,
        int(len(scored) * percentile),
    )

    selected = scored.iloc[:count].copy()

    wins = int(
        (selected["result"] == "WIN").sum()
    )

    losses = int(
        (selected["result"] == "LOSS").sum()
    )

    return {
        "trades": len(selected),
        "wins": wins,
        "losses": losses,
        "win_rate": (
            wins / len(selected)
            if len(selected)
            else 0.0
        ),
        "profit": selected["profit"].sum(),
        "profit_factor": profit_factor(selected),
        "max_drawdown": max_drawdown(selected),
    }


def print_metrics(label, metrics):
    pf = metrics["profit_factor"]

    pf_text = (
        "INF"
        if pf == float("inf")
        else f"{pf:.2f}"
    )

    print(
        f"{label:<6} "
        f"trades={metrics['trades']:>3} | "
        f"wins={metrics['wins']:>3} | "
        f"losses={metrics['losses']:>3} | "
        f"win%={metrics['win_rate']:>6.1%} | "
        f"profit={metrics['profit']:>8.2f} | "
        f"PF={pf_text:>5} | "
        f"MaxDD={metrics['max_drawdown']:>7.2f}"
    )


def main():
    df = load_dataset()

    features = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    minimum_required = (
        TRAIN_WINDOW
        + VALIDATION_WINDOW
        + TEST_WINDOW
    )

    if len(df) < minimum_required:
        raise ValueError(
            f"Need at least {minimum_required} trades, "
            f"got {len(df)}"
        )

    print("=" * 80)
    print("TRADERVAULTAI ROLLING RANK EVALUATION")
    print("=" * 80)

    print(f"Total trades      : {len(df)}")
    print(f"Training window   : {TRAIN_WINDOW}")
    print(f"Validation window : {VALIDATION_WINDOW}")
    print(f"Test window       : {TEST_WINDOW}")
    print()

    results = []

    start = 0
    fold = 1

    while (
        start
        + TRAIN_WINDOW
        + VALIDATION_WINDOW
        + TEST_WINDOW
        <= len(df)
    ):
        train_start = start
        train_end = (
            train_start + TRAIN_WINDOW
        )

        validation_start = train_end
        validation_end = (
            validation_start + VALIDATION_WINDOW
        )

        test_start = validation_end
        test_end = (
            test_start + TEST_WINDOW
        )

        train_df = df.iloc[
            train_start:train_end
        ].copy()

        validation_df = df.iloc[
            validation_start:validation_end
        ].copy()

        test_df = df.iloc[
            test_start:test_end
        ].copy()

        X_train = train_df[features]
        y_train = train_df["target"]

        X_validation = validation_df[features]
        X_test = test_df[features]

        model = build_model()

        model.fit(
            X_train,
            y_train,
        )

        # Validation is used only for model diagnostics.
        validation_probabilities = (
            model.predict_proba(
                X_validation
            )[:, 1]
        )

        test_probabilities = (
            model.predict_proba(
                X_test
            )[:, 1]
        )

        raw_metrics = {
            "trades": len(test_df),
            "wins": int(
                (test_df["result"] == "WIN").sum()
            ),
            "losses": int(
                (test_df["result"] == "LOSS").sum()
            ),
            "win_rate": (
                test_df["result"] == "WIN"
            ).mean(),
            "profit": test_df["profit"].sum(),
            "profit_factor": profit_factor(test_df),
            "max_drawdown": max_drawdown(test_df),
        }

        print()
        print("=" * 80)
        print(f"ROLLING FOLD {fold}")
        print("=" * 80)

        print(
            f"TRAIN      : "
            f"{train_df.trade_date.min().date()} "
            f"to "
            f"{train_df.trade_date.max().date()} "
            f"({len(train_df)} trades)"
        )

        print(
            f"VALIDATION : "
            f"{validation_df.trade_date.min().date()} "
            f"to "
            f"{validation_df.trade_date.max().date()} "
            f"({len(validation_df)} trades)"
        )

        print(
            f"TEST       : "
            f"{test_df.trade_date.min().date()} "
            f"to "
            f"{test_df.trade_date.max().date()} "
            f"({len(test_df)} trades)"
        )

        print()
        print_metrics("RAW", raw_metrics)

        for percentile in PERCENTILES:
            metrics = evaluate_percentile(
                test_df,
                test_probabilities,
                percentile,
            )

            print(
                f"TOP {int(percentile * 100):>2}%"
            )
            print_metrics(
                "",
                metrics,
            )

            results.append(
                {
                    "fold": fold,
                    "percentile": percentile,
                    "raw_profit": raw_metrics["profit"],
                    "raw_pf": raw_metrics["profit_factor"],
                    "raw_max_dd": raw_metrics["max_drawdown"],
                    "ml_trades": metrics["trades"],
                    "ml_wins": metrics["wins"],
                    "ml_losses": metrics["losses"],
                    "ml_profit": metrics["profit"],
                    "ml_pf": metrics["profit_factor"],
                    "ml_max_dd": metrics["max_drawdown"],
                }
            )

        start += TEST_WINDOW
        fold += 1

    if not results:
        print("No valid rolling folds.")
        return

    results_df = pd.DataFrame(results)

    print()
    print("=" * 80)
    print("ROLLING RANK SUMMARY")
    print("=" * 80)

    summary = (
        results_df
        .groupby("percentile")
        .agg(
            folds=("fold", "count"),
            selected_trades=("ml_trades", "sum"),
            wins=("ml_wins", "sum"),
            losses=("ml_losses", "sum"),
            total_profit=("ml_profit", "sum"),
            average_pf=("ml_pf", "mean"),
            average_max_dd=("ml_max_dd", "mean"),
        )
        .reset_index()
    )

    summary["win_rate"] = (
        summary["wins"]
        / summary["selected_trades"]
    )

    print(
        summary.to_string(
            index=False,
            float_format=lambda x: f"{x:.3f}",
        )
    )

    print()
    print("RAW TOTAL TEST PROFIT:")

    raw_profit = (
        results_df
            .drop_duplicates(subset=["fold"])["raw_profit"]
            .sum()
    )

    print(f"{raw_profit:.2f}")

if __name__ == "__main__":
    main()