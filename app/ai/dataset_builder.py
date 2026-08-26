import pandas as pd


class DatasetBuilder:

    def __init__(self):
        self.rows = []

    def add(self, features):

        self.rows.append(features)

    def dataframe(self):

        return pd.DataFrame(self.rows)

    def export_csv(
        self,
        filename="training_dataset.csv",
    ):

        df = self.dataframe()

        df.to_csv(
            filename,
            index=False,
        )

        return filename