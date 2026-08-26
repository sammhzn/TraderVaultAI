from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATASET = Path("training_dataset.csv")

TRAIN_WINDOW = 80
VALIDATION_WINDOW = 20
TEST_WINDOW = 15

TOP_PERCENTILE = 0.20


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
        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

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
        column
        for column in required
        if column not in df.columns
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


def raw_metrics(df):
    if df.empty:
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
        (df["result"] == "WIN").sum()
    )

    losses = int(
        (df["result"] == "LOSS").sum()
    )

    return {
        "trades": len(df),
        "wins": wins,
        "losses": losses,
        "win_rate": wins / len(df),
        "profit": df["profit"].sum(),
        "profit_factor": profit_factor(df),
        "max_drawdown": max_drawdown(df),
    }


def rank_metrics(
    df,
    probabilities,
):
    if df.empty:
        return raw_metrics(df)

    scored = df.copy()

    scored["model_score"] = pd.Series(
        probabilities,
        index=scored.index,
        dtype="float64",
    )

    scored = scored.sort_values(
        "model_score",
        ascending=False,
    )

    count = max(
        1,
        int(len(scored) * TOP_PERCENTILE),
    )

    selected = scored.iloc[
        :count
    ].copy()

    return raw_metrics(selected)


def should_activate_ml(
    validation_df,
    validation_probabilities,
):
    """
    Activate ML only when it shows better risk-adjusted
    validation quality than the raw strategy.

    Requirements:
      - at least 3 selected trades
      - better or equal profit factor
      - lower maximum drawdown
    """

    raw = raw_metrics(
        validation_df
    )

    ranked = rank_metrics(
        validation_df,
        validation_probabilities,
    )

    if ranked["trades"] < 3:
        return False, raw, ranked

    pf_improvement = (
        ranked["profit_factor"]
        >= raw["profit_factor"]
    )

    drawdown_improvement = (
        ranked["max_drawdown"]
        < raw["max_drawdown"]
    )

    activate = (
        pf_improvement
        and drawdown_improvement
    )

    return (
        activate,
        raw,
        ranked,
    )


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
        f"{label:<12}"
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
            f"Need at least {minimum_required} "
            f"trades, got {len(df)}"
        )

    print("=" * 80)
    print(
        "TRADERVAULTAI ADAPTIVE "
        "ROLLING ML FILTER"
    )
    print("=" * 80)

    print(
        f"Total trades       : {len(df)}"
    )
    print(
        f"Training window    : {TRAIN_WINDOW}"
    )
    print(
        f"Validation window  : {VALIDATION_WINDOW}"
    )
    print(
        f"Test window        : {TEST_WINDOW}"
    )
    print(
        f"Top percentile     : {TOP_PERCENTILE:.0%}"
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

        X_train = train_df[features]
        y_train = train_df["target"]

        X_validation = validation_df[features]
        X_test = test_df[features]

        model = build_model()

        model.fit(
            X_train,
            y_train,
        )

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
        # Decide whether ML is trusted for the next test
        # period.
        #
        # This decision uses VALIDATION ONLY.
        # --------------------------------------------------

        activate_ml, validation_raw, validation_ml = (
            should_activate_ml(
                validation_df,
                validation_probabilities,
            )
        )

        raw_test = raw_metrics(
            test_df
        )

        if activate_ml:
            test_result = rank_metrics(
                test_df,
                test_probabilities,
            )
        else:
            test_result = raw_test

        results.append(
            {
                "fold": fold,
                "ml_active": activate_ml,
                "validation_raw_profit":
                    validation_raw["profit"],
                "validation_ml_profit":
                    validation_ml["profit"],
                "test_raw_profit":
                    raw_test["profit"],
                "test_result_profit":
                    test_result["profit"],
                "test_raw_pf":
                    raw_test["profit_factor"],
                "test_result_pf":
                    test_result["profit_factor"],
                "test_raw_dd":
                    raw_test["max_drawdown"],
                "test_result_dd":
                    test_result["max_drawdown"],
                "test_raw_trades":
                    raw_test["trades"],
                "test_result_trades":
                    test_result["trades"],
                "test_result_wins":
                    test_result["wins"],
                "test_result_losses":
                    test_result["losses"],
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
            f"ML ACTIVE: {'YES' if activate_ml else 'NO'}"
        )

        print(
            "Validation:"
        )
        print_metrics(
            "RAW",
            validation_raw,
        )
        print_metrics(
            "ML",
            validation_ml,
        )

        print()
        print(
            "Unseen test:"
        )
        print_metrics(
            "RAW",
            raw_test,
        )
        print_metrics(
            "ADAPTIVE",
            test_result,
        )

        start += TEST_WINDOW
        fold += 1

    if not results:
        print()
        print(
            "No valid folds."
        )
        return

    results_df = pd.DataFrame(
        results
    )

    adaptive_equity = (
        results_df[
            "test_result_profit"
        ].cumsum()
    )

    adaptive_peak = (
        adaptive_equity.cummax()
    )

    adaptive_dd = (
        adaptive_equity
        - adaptive_peak
    )

    raw_equity = (
        results_df[
            "test_raw_profit"
        ].cumsum()
    )

    raw_peak = (
        raw_equity.cummax()
    )

    raw_dd = (
        raw_equity
        - raw_peak
    )

    print()
    print("=" * 80)
    print(
        "ADAPTIVE ROLLING SUMMARY"
    )
    print("=" * 80)

    print(
        f"Raw total profit       : "
        f"{results_df['test_raw_profit'].sum():.2f}"
    )

    print(
        f"Adaptive total profit  : "
        f"{results_df['test_result_profit'].sum():.2f}"
    )

    print(
        f"Raw aggregate MaxDD    : "
        f"{abs(raw_dd.min()):.2f}"
    )

    print(
        f"Adaptive aggregate DD  : "
        f"{abs(adaptive_dd.min()):.2f}"
    )

    print(
        f"ML activated folds     : "
        f"{int(results_df['ml_active'].sum())}"
        f"/{len(results_df)}"
    )

    print(
        f"Adaptive trades        : "
        f"{results_df['test_result_trades'].sum()}"
    )

    print()

    print(
        results_df[
            [
                "fold",
                "ml_active",
                "validation_raw_profit",
                "validation_ml_profit",
                "test_raw_profit",
                "test_result_profit",
                "test_raw_pf",
                "test_result_pf",
                "test_raw_trades",
                "test_result_trades",
            ]
        ].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()