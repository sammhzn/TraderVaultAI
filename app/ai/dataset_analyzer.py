import pandas as pd


class DatasetAnalyzer:

    def __init__(self, filename="training_dataset.csv"):
        self.filename = filename

    def load(self):
        return pd.read_csv(self.filename)

    def summary(self):

        df = self.load()

        total = len(df)

        wins = len(
            df[df["result"] == "WIN"]
        )

        losses = len(
            df[df["result"] == "LOSS"]
        )

        win_rate = (
            (wins / total) * 100
            if total > 0
            else 0
        )

        total_profit = df["profit"].sum()

        average_profit = (
            df["profit"].mean()
            if total > 0
            else 0
        )

        return {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "total_profit": round(total_profit, 2),
            "average_profit": round(average_profit, 2),
        }

    def by_regime(self):

        df = self.load()

        return (
            df.groupby("market_regime")
            .agg(
                trades=("result", "count"),
                wins=("result", lambda x: (x == "WIN").sum()),
                losses=("result", lambda x: (x == "LOSS").sum()),
                profit=("profit", "sum"),
            )
            .reset_index()
        )

    def by_direction(self):

        df = self.load()

        return (
            df.groupby("direction")
            .agg(
                trades=("result", "count"),
                wins=("result", lambda x: (x == "WIN").sum()),
                losses=("result", lambda x: (x == "LOSS").sum()),
                profit=("profit", "sum"),
            )
            .reset_index()
        )

    def by_hour(self):

        df = self.load()

        return (
            df.groupby("hour")
            .agg(
                trades=("result", "count"),
                wins=("result", lambda x: (x == "WIN").sum()),
                losses=("result", lambda x: (x == "LOSS").sum()),
                profit=("profit", "sum"),
            )
            .reset_index()
            .sort_values("profit", ascending=False)
        )