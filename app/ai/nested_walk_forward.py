from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATASET = Path("training_dataset.csv")

THRESHOLDS = [
    0.45,
    0.50,
    0.55,
    0.60,
]

# ----------------------------------------------------------
# Features
# ----------------------------------------------------------

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


# ----------------------------------------------------------
# Dataset
# ----------------------------------------------------------

def load_dataset():
    if not DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

    df = pd.read_csv(DATASET)

    required_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
        + [
            "trade_date",
            "result",
            "profit",
        ]
    )

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing dataset columns: {missing}"
        )

    df["trade_date"] = pd.to_datetime(
        df["trade_date"],
        errors="coerce",
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


# ----------------------------------------------------------
# Model
# ----------------------------------------------------------

def build_model():
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


# ----------------------------------------------------------
# Metrics
# ----------------------------------------------------------

def profit_factor(df):
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
        if gross_profit > 0:
            return float("inf")

        return 0.0

    return gross_profit / gross_loss


def max_drawdown(df):
    if df.empty:
        return 0.0

    ordered = df.sort_values(
        ["trade_date", "hour"]
    )

    equity = ordered["profit"].cumsum()
    peak = equity.cummax()

    drawdown = equity - peak

    return abs(drawdown.min())


def evaluate_threshold(
    df,
    probabilities,
    threshold,
):
    selected = df[
        probabilities >= threshold
    ].copy()

    if selected.empty:
        return {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "profit": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
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
        "profit": selected["profit"].sum(),
        "profit_factor": profit_factor(
            selected
        ),
        "max_drawdown": max_drawdown(
            selected
        ),
        "win_rate": (
            wins / len(selected)
        ),
    }


# ----------------------------------------------------------
# Threshold selection
# ----------------------------------------------------------

def choose_threshold(
    validation_df,
    validation_probabilities,
):
    """
    Choose the threshold ONLY from validation data.

    Priority:
    1. Positive validation profit
    2. Higher validation profit factor
    3. More trades
    4. Higher win rate

    A minimum of 3 trades is required before a
    threshold can be considered a strong candidate.
    """

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

    positive_candidates = [
        candidate
        for candidate in candidates
        if (
            candidate["profit"] > 0
            and candidate["trades"] >= 3
        )
    ]

    if positive_candidates:

        positive_candidates.sort(
            key=lambda item: (
                item["profit_factor"],
                item["profit"],
                item["trades"],
                item["win_rate"],
            ),
            reverse=True,
        )

        return (
            positive_candidates[0],
            candidates,
        )

    # If no threshold is profitable,
    # choose the least-bad one by profit.
    candidates.sort(
        key=lambda item: (
            item["profit"],
            item["profit_factor"],
            item["trades"],
            item["win_rate"],
        ),
        reverse=True,
    )

    return (
        candidates[0],
        candidates,
    )


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main():

    df = load_dataset()

    feature_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    print("=" * 75)
    print(
        "TRADERVAULTAI NESTED WALK-FORWARD VALIDATION"
    )
    print("=" * 75)

    print(
        f"Total trades: {len(df)}"
    )

    print()

    # ------------------------------------------------------
    # Outer folds
    #
    # Each fold is:
    #
    # TRAIN       VALIDATION       TEST
    # 0% - 40%    40% - 50%       50% - 60%
    #
    # 0% - 50%    50% - 60%       60% - 70%
    #
    # etc.
    # ------------------------------------------------------

    fold_boundaries = [
        (0.40, 0.50, 0.60),
        (0.50, 0.60, 0.70),
        (0.60, 0.70, 0.80),
        (0.70, 0.80, 0.90),
        (0.80, 0.90, 1.00),
    ]

    results = []

    for fold_number, (
        train_end_pct,
        validation_end_pct,
        test_end_pct,
    ) in enumerate(
        fold_boundaries,
        start=1,
    ):

        train_end_idx = int(
            len(df) * train_end_pct
        )

        validation_end_idx = int(
            len(df) * validation_end_pct
        )

        test_end_idx = int(
            len(df) * test_end_pct
        )

        train_df = df.iloc[
            :train_end_idx
        ].copy()

        validation_df = df.iloc[
            train_end_idx:validation_end_idx
        ].copy()

        test_df = df.iloc[
            validation_end_idx:test_end_idx
        ].copy()

        if (
            len(train_df) < 30
            or len(validation_df) < 5
            or len(test_df) < 5
        ):
            print(
                f"Skipping fold {fold_number}: "
                "not enough observations."
            )
            continue

        # --------------------------------------------------
        # Training
        # --------------------------------------------------

        X_train = train_df[
            feature_columns
        ]

        y_train = train_df[
            "target"
        ]

        X_validation = validation_df[
            feature_columns
        ]

        X_test = test_df[
            feature_columns
        ]

        model = build_model()

        model.fit(
            X_train,
            y_train,
        )

        # --------------------------------------------------
        # Validation predictions
        # --------------------------------------------------

        validation_probabilities = (
            model.predict_proba(
                X_validation
            )[:, 1]
        )

        # --------------------------------------------------
        # Select threshold from VALIDATION ONLY
        # --------------------------------------------------

        selected_threshold, candidates = (
            choose_threshold(
                validation_df,
                validation_probabilities,
            )
        )

        threshold = (
            selected_threshold["threshold"]
        )

        # --------------------------------------------------
        # Test predictions
        # --------------------------------------------------

        test_probabilities = (
            model.predict_proba(
                X_test
            )[:, 1]
        )

        # --------------------------------------------------
        # Raw test performance
        # --------------------------------------------------

        raw_test_metrics = {
            "trades": len(test_df),
            "wins": int(
                (
                    test_df["result"]
                    == "WIN"
                ).sum()
            ),
            "losses": int(
                (
                    test_df["result"]
                    == "LOSS"
                ).sum()
            ),
            "profit": test_df[
                "profit"
            ].sum(),
            "profit_factor": profit_factor(
                test_df
            ),
            "max_drawdown": max_drawdown(
                test_df
            ),
            "win_rate": (
                test_df["result"]
                == "WIN"
            ).mean(),
        }

        # --------------------------------------------------
        # ML test performance
        # --------------------------------------------------

        ml_test_metrics = evaluate_threshold(
            test_df,
            test_probabilities,
            threshold,
        )

        results.append(
            {
                "fold": fold_number,
                "threshold": threshold,

                "raw_trades":
                    raw_test_metrics["trades"],

                "raw_profit":
                    raw_test_metrics["profit"],

                "raw_pf":
                    raw_test_metrics[
                        "profit_factor"
                    ],

                "raw_max_dd":
                    raw_test_metrics[
                        "max_drawdown"
                    ],

                "ml_trades":
                    ml_test_metrics["trades"],

                "ml_wins":
                    ml_test_metrics["wins"],

                "ml_losses":
                    ml_test_metrics["losses"],

                "ml_profit":
                    ml_test_metrics["profit"],

                "ml_pf":
                    ml_test_metrics[
                        "profit_factor"
                    ],

                "ml_max_dd":
                    ml_test_metrics[
                        "max_drawdown"
                    ],
            }
        )

        # --------------------------------------------------
        # Print fold
        # --------------------------------------------------

        print("=" * 75)
        print(
            f"FOLD {fold_number}"
        )
        print("=" * 75)

        print(
            "TRAIN      : "
            f"{train_df.trade_date.min().date()} "
            "to "
            f"{train_df.trade_date.max().date()} "
            f"({len(train_df)} trades)"
        )

        print(
            "VALIDATION : "
            f"{validation_df.trade_date.min().date()} "
            "to "
            f"{validation_df.trade_date.max().date()} "
            f"({len(validation_df)} trades)"
        )

        print(
            "TEST       : "
            f"{test_df.trade_date.min().date()} "
            "to "
            f"{test_df.trade_date.max().date()} "
            f"({len(test_df)} trades)"
        )

        print()

        print(
            "Validation threshold candidates:"
        )

        for candidate in candidates:

            pf = candidate[
                "profit_factor"
            ]

            pf_text = (
                "INF"
                if pf == float("inf")
                else f"{pf:.2f}"
            )

            print(
                f"  {candidate['threshold']:.2f} | "
                f"trades={candidate['trades']:>2} | "
                f"wins={candidate['wins']:>2} | "
                f"losses={candidate['losses']:>2} | "
                f"profit={candidate['profit']:>7.2f} | "
                f"PF={pf_text}"
            )

        print()

        print(
            f"CHOSEN THRESHOLD : "
            f"{threshold:.2f}"
        )

        raw_pf = raw_test_metrics[
            "profit_factor"
        ]

        raw_pf_text = (
            "INF"
            if raw_pf == float("inf")
            else f"{raw_pf:.2f}"
        )

        ml_pf = ml_test_metrics[
            "profit_factor"
        ]

        ml_pf_text = (
            "INF"
            if ml_pf == float("inf")
            else f"{ml_pf:.2f}"
        )

        print(
            f"RAW TEST : "
            f"trades={raw_test_metrics['trades']} | "
            f"profit={raw_test_metrics['profit']:.2f} | "
            f"PF={raw_pf_text} | "
            f"MaxDD={raw_test_metrics['max_drawdown']:.2f}"
        )

        print(
            f"ML TEST  : "
            f"trades={ml_test_metrics['trades']} | "
            f"wins={ml_test_metrics['wins']} | "
            f"losses={ml_test_metrics['losses']} | "
            f"profit={ml_test_metrics['profit']:.2f} | "
            f"PF={ml_pf_text} | "
            f"MaxDD={ml_test_metrics['max_drawdown']:.2f}"
        )

        print()

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    if not results:
        print(
            "No valid folds were produced."
        )
        return

    results_df = pd.DataFrame(
        results
    )

    print("=" * 75)
    print(
        "NESTED WALK-FORWARD SUMMARY"
    )
    print("=" * 75)

    raw_total_profit = (
        results_df[
            "raw_profit"
        ].sum()
    )

    ml_total_profit = (
        results_df[
            "ml_profit"
        ].sum()
    )

    # Build fold-level equity curves.
    raw_equity = (
        results_df[
            "raw_profit"
        ].cumsum()
    )

    ml_equity = (
        results_df[
            "ml_profit"
        ].cumsum()
    )

    raw_peak = raw_equity.cummax()
    ml_peak = ml_equity.cummax()

    raw_drawdown = (
        raw_equity - raw_peak
    )

    ml_drawdown = (
        ml_equity - ml_peak
    )

    raw_max_dd = abs(
        raw_drawdown.min()
    )

    ml_max_dd = abs(
        ml_drawdown.min()
    )

    finite_raw_pf = (
        results_df[
            "raw_pf"
        ]
        .replace(
            float("inf"),
            pd.NA,
        )
        .dropna()
    )

    finite_ml_pf = (
        results_df[
            "ml_pf"
        ]
        .replace(
            float("inf"),
            pd.NA,
        )
        .dropna()
    )

    print(
        f"Raw total profit     : "
        f"{raw_total_profit:.2f}"
    )

    print(
        f"ML total profit      : "
        f"{ml_total_profit:.2f}"
    )

    print(
        f"Raw average PF       : "
        f"{finite_raw_pf.mean():.2f}"
    )

    print(
        f"ML average PF        : "
        f"{finite_ml_pf.mean():.2f}"
    )

    print(
        f"Raw aggregate MaxDD  : "
        f"{raw_max_dd:.2f}"
    )

    print(
        f"ML aggregate MaxDD   : "
        f"{ml_max_dd:.2f}"
    )

    print(
        f"ML selected trades   : "
        f"{results_df['ml_trades'].sum()}"
    )

    print()

    print(
        "Fold comparison:"
    )

    print(
        results_df[
            [
                "fold",
                "threshold",
                "raw_trades",
                "raw_profit",
                "raw_pf",
                "raw_max_dd",
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