from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


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


def load_dataset():
    if not DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

    df = pd.read_csv(DATASET)

    required = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
        + ["trade_date", "result"]
    )

    missing = [
        column
        for column in required
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

    df = df.dropna(
        subset=["trade_date", "result"]
    ).sort_values(
        ["trade_date", "hour"]
    ).reset_index(drop=True)

    df["target"] = (
        df["result"]
        .eq("WIN")
        .astype(int)
    )

    return df


def main():

    df = load_dataset()

    # --------------------------------------------------
    # Chronological split
    #
    # IMPORTANT:
    # The final 30% is NOT used for training.
    # --------------------------------------------------

    split_index = int(len(df) * 0.70)

    train_df = df.iloc[:split_index].copy()
    test_df = df.iloc[split_index:].copy()

    print("=" * 60)
    print("TRADERVAULTAI ML TRAINING")
    print("=" * 60)

    print(
        f"Total trades     : {len(df)}"
    )

    print(
        f"Training trades  : {len(train_df)}"
    )

    print(
        f"Test trades      : {len(test_df)}"
    )

    print()

    print(
        "Training period  : "
        f"{train_df.trade_date.min().date()} "
        "to "
        f"{train_df.trade_date.max().date()}"
    )

    print(
        "Test period      : "
        f"{test_df.trade_date.min().date()} "
        "to "
        f"{test_df.trade_date.max().date()}"
    )

    print()

    X_train = train_df[
        NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ]

    y_train = train_df["target"]

    X_test = test_df[
        NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ]

    y_test = test_df["target"]

    # --------------------------------------------------
    # Preprocessing
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Logistic regression
    # --------------------------------------------------

    model = Pipeline(
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

    # --------------------------------------------------
    # Train ONLY on training period
    # --------------------------------------------------

    model.fit(
        X_train,
        y_train,
    )

    # --------------------------------------------------
    # Evaluate on untouched test period
    # --------------------------------------------------

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    print()
    print("=" * 60)
    print("OUT-OF-SAMPLE MODEL RESULTS")
    print("=" * 60)

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "LOSS",
                "WIN",
            ],
            zero_division=0,
        )
    )

    print("Confusion matrix:")
    print(
        confusion_matrix(
            y_test,
            predictions,
        )
    )

    print()
    print("Predicted WIN probabilities:")
    print(
        pd.Series(
            probabilities
        ).describe().round(3)
    )

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print()
    print(
        f"Model saved to: {MODEL_PATH}"
    )


if __name__ == "__main__":
    main()