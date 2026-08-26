import MetaTrader5 as mt5

from app.backtesting.backtest_runner import BacktestRunner


def main():

    print("=" * 60)
    print("TraderVaultAI Backtest")
    print("=" * 60)

    # --------------------------------------------------
    # Initialize MetaTrader 5
    # --------------------------------------------------

    if not mt5.initialize():

        print("MT5 initialization failed")
        print("Error:", mt5.last_error())

        return

    try:

        runner = BacktestRunner()

        result = runner.run(
            symbol="XAUUSD",
            timeframe=mt5.TIMEFRAME_M1,
            bars=250000,
        )

        print()
        print("=" * 60)
        print("BACKTEST RESULT")
        print("=" * 60)

        print(
            f"Candles loaded : {result['candles']}"
        )

        print(
            f"Decisions      : {result['decisions']}"
        )

        print(
            f"Open positions : {result['positions']}"
        )

        print()
        print(result["report"])

        print("=" * 60)

    finally:

        mt5.shutdown()


if __name__ == "__main__":
    main()