import numpy as np
import pandas as pd


class DataRace:
    def __init__(self):
        self.df_raw = None
        self.df_processed = None
        self.df_final = None

    def __get_df_raw(self, data_session: object) -> pd.DataFrame:
        """
        Retrieve race session data from a DataFrame.

        Args:
            data_session (object): The raw race session data.

        Returns:
            pd.DataFrame: A DataFrame containing the relevant columns from the race data.
        """

        col_required = [
            "DriverId",
            "LastName",
            "FirstName",
            "TeamName",
            "ClassifiedPosition",
            "Time",
        ]

        try:
            self.df_raw = data_session.results[col_required].copy()
        except KeyError as e:
            raise ValueError(f"Session data doesn't contain the required columns: {e}.")

        return self.df_raw

    def __get_df_processed(
        self, df_raw: pd.DataFrame, year: int, round: int
    ) -> pd.DataFrame:
        """
        Process the raw race data and return a processed DataFrame.

        Args:
            df_raw (pd.DataFrame): The raw race data DataFrame.
            year (int): The year of the session.
            round (int): The round number of the session.

        Returns:
            pd.DataFrame: The processed race data DataFrame.
        """

        self.df_processed = df_raw.copy().reset_index(drop=True)

        self.df_processed["year"] = year
        self.df_processed["round"] = round
        self.df_processed["session"] = "Race"

        self.df_processed.columns = self.df_processed.columns.str.lower()
        self.df_processed.rename(
            columns={
                "classifiedposition": "position",
                "driverid": "id_driver",
                "lastname": "name_driver_last",
                "firstname": "name_driver_first",
                "teamname": "name_team",
            },
            inplace=True,
        )
        self.df_processed.loc[1:, "time"] = (
            self.df_processed.loc[1:, "time"] + self.df_processed.loc[0, "time"]
        )
        self.df_processed["position"] = self.df_processed["position"].astype(str)
        self.df_processed.loc[self.df_processed["time"].isna(), "position"] = "DNF"
        self.df_processed["time"] = (
            self.df_processed["time"].fillna(np.nan).replace([np.nan], [None])
        )

        return self.df_processed

    def __get_df_final(self, df_processed: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a DataFrame containing the final race data.

        Args:
            df_processed (pd.DataFrame): The processed DataFrame containing race data.

        Returns:
            pd.DataFrame: The DataFrame containing the final race data.
        """

        self.df_final = df_processed[
            [
                "year",
                "round",
                "id_driver",
                "name_driver_last",
                "name_driver_first",
                "name_team",
                "session",
                "position",
                "time",
            ]
        ]

        return self.df_final

    def get_df_race(self, data_session: object, year: int, round: int) -> pd.DataFrame:
        """
        Retrieves the final DataFrame containing the race session data.

        Args:
            data_session (object): The raw race session data.
            year (int): The year of the session.
            round (int): The round number of the session.

        Returns:
            pd.DataFrame: A DataFrame containing the race session data.
        """

        df_raw = self.__get_df_raw(data_session)
        df_processed = self.__get_df_processed(df_raw, year, round)
        df_final = self.__get_df_final(df_processed)

        return df_final
