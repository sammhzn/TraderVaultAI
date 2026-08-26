from app.ai.dataset_analyzer import DatasetAnalyzer


def main():

    analyzer = DatasetAnalyzer(
        "training_dataset.csv"
    )

    # ---------------------------------------------
    # Overall summary
    # ---------------------------------------------

    summary = analyzer.summary()

    print("\n==============================")
    print("TRADER VAULT AI DATASET")
    print("==============================")

    print(f"Total trades : {summary['total_trades']}")
    print(f"Wins         : {summary['wins']}")
    print(f"Losses       : {summary['losses']}")
    print(f"Win rate     : {summary['win_rate']}%")
    print(f"Total profit : {summary['total_profit']}")
    print(f"Avg profit   : {summary['average_profit']}")

    # ---------------------------------------------
    # Market regime
    # ---------------------------------------------

    print("\n==============================")
    print("PERFORMANCE BY MARKET REGIME")
    print("==============================")

    regime = analyzer.by_regime()

    print(regime.to_string(index=False))

    # ---------------------------------------------
    # Direction
    # ---------------------------------------------

    print("\n==============================")
    print("PERFORMANCE BY DIRECTION")
    print("==============================")

    direction = analyzer.by_direction()

    print(direction.to_string(index=False))

    # ---------------------------------------------
    # Hour
    # ---------------------------------------------

    print("\n==============================")
    print("PERFORMANCE BY HOUR")
    print("==============================")

    hours = analyzer.by_hour()

    print(hours.to_string(index=False))


if __name__ == "__main__":
    main()