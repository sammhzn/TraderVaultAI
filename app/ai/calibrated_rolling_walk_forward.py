from pathlib import Path

import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATASET = Path("training_dataset.csv")

THRESHOLDS = [0.45, 0.50, 0.55, 0.60]

TRAIN_WINDOW = 60
VALIDATION_WINDOW = 20
TEST_WINDOW = 15


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
        + [
            "trade_date",
            "result",
            "profit",
        ]
    )

    missing = [
        c for c in required
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    df = (
        df.dropna(
            subset=[
                "trade_date",
                "result",
                "profit",
            ]
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

    return df


def build_base_model():
    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
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
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
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
            (
                "preprocessor",
                preprocessor,
            ),
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


def fit_calibrated_model(
    train_df,
):
    """
    Fit the base model on the training window.

    Calibration is then performed using the validation
    window supplied later through cross-validation inside
    CalibratedClassifierCV.

    Important:
    We do not use the final test window for fitting.
    """

    X_train = train_df[
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y_train = train_df["target"]

    base_model = build_base_model()

    # With only 60 observations, 3-fold calibration is a
    # reasonable minimum while keeping the fold sizes usable.
    calibrated = CalibratedClassifierCV(
        estimator=base_model,
        method="sigmoid",
        cv=3,
    )

    calibrated.fit(
        X_train,
        y_train,
    )

    return calibrated


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

    return abs(
        (equity - peak).min()
    )


def evaluate_threshold(
    df,
    probabilities,
    threshold,
):
    probabilities = pd.Series(
        probabilities,
        index=df.index,
        dtype="float64",
    )

    selected = df[
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
            "max_drawdown": 0.0,
        }

    wins = int(
        (
            selected["result"] == "WIN"
        ).sum()
    )

    losses = int(
        (
            selected["result"] == "LOSS"
        ).sum()
    )

    return {
        "trades": len(selected),
        "wins": wins,
        "losses": losses,
        "win_rate": wins / len(selected),
        "profit": selected["profit"].sum(),
        "profit_factor": profit_factor(
            selected
        ),
        "max_drawdown": max_drawdown(
            selected
        ),
    }


def choose_threshold(
    validation_df,
    validation_probabilities,
):
    candidates = []

    for threshold in THRESHOLDS:
        metrics = evaluate_threshold(
            validation_df,
            validation_probabilities,
            threshold,
        )

        candidates.append(
            {
                "threshold": threshold,
                **metrics,
            }
        )

    good = [
        x for x in candidates
        if (
            x["profit"] > 0
            and x["trades"] >= 3
        )
    ]

    if good:
        good.sort(
            key=lambda x: (
                x["profit"],
                x["profit_factor"],
                x["win_rate"],
            ),
            reverse=True,
        )

        return good[0]["threshold"]

    candidates.sort(
        key=lambda x: (
            x["profit"],
            x["profit_factor"],
            x["trades"],
        ),
        reverse=True,
    )

    return candidates[0]["threshold"]


def print_metrics(
    label,
    metrics,
):
    pf = metrics["profit_factor"]

    pf_text = (
        "INF"
        if pf == float("inf")
        else f"{pf:.2f}"
    )

    print(
        f"{label:<5} "
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
            f"Need at least "
            f"{minimum_required} trades, "
            f"got {len(df)}"
        )

    print("=" * 80)
    print(
        "TRADERVAULTAI CALIBRATED "
        "ROLLING WALK-FORWARD"
    )
    print("=" * 80)

    print(
        f"Total trades      : {len(df)}"
    )
    print(
        f"Training window   : {TRAIN_WINDOW}"
    )
    print(
        f"Validation window : {VALIDATION_WINDOW}"
    )
    print(
        f"Test window       : {TEST_WINDOW}"
    )

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
            train_start
            + TRAIN_WINDOW
        )

        validation_start = train_end
        validation_end = (
            validation_start
            + VALIDATION_WINDOW
        )

        test_start = validation_end
        test_end = (
            test_start
            + TEST_WINDOW
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

        # --------------------------------------------------
        # Train a calibrated model using ONLY the training
        # window.
        # --------------------------------------------------

        model = fit_calibrated_model(
            train_df
        )

        X_validation = validation_df[
            features
        ]

        X_test = test_df[
            features
        ]

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

        # --------------------------------------------------
        # Threshold selection occurs ONLY on validation.
        # --------------------------------------------------

        threshold = choose_threshold(
            validation_df,
            validation_probabilities,
        )

        # --------------------------------------------------
        # Raw test metrics.
        # --------------------------------------------------

        raw_probabilities = pd.Series(
            [1.0] * len(test_df),
            index=test_df.index,
            dtype="float64",
        )

        raw_metrics = evaluate_threshold(
            test_df,
            raw_probabilities,
            0.0,
        )

        # --------------------------------------------------
        # Calibrated ML test metrics.
        # --------------------------------------------------

        ml_metrics = evaluate_threshold(
            test_df,
            test_probabilities,
            threshold,
        )

        results.append(
            {
                "fold": fold,
                "threshold": threshold,

                "raw_trades":
                    raw_metrics["trades"],
                "raw_profit":
                    raw_metrics["profit"],
                "raw_pf":
                    raw_metrics["profit_factor"],
                "raw_max_dd":
                    raw_metrics["max_drawdown"],

                "ml_trades":
                    ml_metrics["trades"],
                "ml_wins":
                    ml_metrics["wins"],
                "ml_losses":
                    ml_metrics["losses"],
                "ml_profit":
                    ml_metrics["profit"],
                "ml_pf":
                    ml_metrics["profit_factor"],
                "ml_max_dd":
                    ml_metrics["max_drawdown"],
            }
        )

        print()
        print("=" * 80)
        print(
            f"FOLD {fold}"
        )
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
        print(
            f"Chosen threshold: "
            f"{threshold:.2f}"
        )

        print_metrics(
            "RAW",
            raw_metrics,
        )

        print_metrics(
            "ML",
            ml_metrics,
        )

        print(
            "Probability range: "
            f"{test_probabilities.min():.3f} "
            f"to "
            f"{test_probabilities.max():.3f}"
        )

        start += TEST_WINDOW
        fold += 1

    if not results:
        print(
            "No valid folds."
        )
        return

    results_df = pd.DataFrame(
        results
    )

    raw_total = results_df[
        "raw_profit"
    ].sum()

    ml_total = results_df[
        "ml_profit"
    ].sum()

    raw_equity = results_df[
        "raw_profit"
    ].cumsum()

    ml_equity = results_df[
        "ml_profit"
    ].cumsum()

    raw_dd = (
        raw_equity
        - raw_equity.cummax()
    )

    ml_dd = (
        ml_equity
        - ml_equity.cummax()
    )

    raw_pfs = (
        results_df["raw_pf"]
        .replace(
            float("inf"),
            pd.NA,
        )
        .dropna()
    )

    ml_pfs = (
        results_df["ml_pf"]
        .replace(
            float("inf"),
            pd.NA,
        )
        .dropna()
    )

    print()
    print("=" * 80)
    print(
        "CALIBRATED ROLLING SUMMARY"
    )
    print("=" * 80)

    print(
        f"Raw total profit    : "
        f"{raw_total:.2f}"
    )

    print(
        f"ML total profit     : "
        f"{ml_total:.2f}"
    )

    print(
        f"Raw average PF      : "
        f"{raw_pfs.mean():.2f}"
    )

    print(
        f"ML average PF       : "
        f"{ml_pfs.mean():.2f}"
    )

    print(
        f"Raw aggregate MaxDD : "
        f"{abs(raw_dd.min()):.2f}"
    )

    print(
        f"ML aggregate MaxDD  : "
        f"{abs(ml_dd.min()):.2f}"
    )

    print(
        f"ML selected trades  : "
        f"{results_df['ml_trades'].sum()}"
    )

    print()

    print(
        results_df[
            [
                "fold",
                "threshold",
                "raw_profit",
                "raw_pf",
                "ml_trades",
                "ml_wins",
                "ml_losses",
                "ml_profit",
                "ml_pf",
                "ml_max_dd",
            ]
        ].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()