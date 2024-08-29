import pandas as pd


class DataQuali:
    def __init__(self):
        self.df_raw = None
        self.df_processed = None
        self.df_final = None

    def __get_df_raw(self, data_session: object) -> pd.DataFrame:
        """
        Retrieve qualifying session data from a DataFrame.

        Args:
            data_session (object): The raw qualifying session data.

        Returns:
            pd.DataFrame: A DataFrame containing the relevant columns from the qualifying data.
        """

        col_required = [
            "Q1",
            "Q2",
            "Q3",
            "DriverId",
            "LastName",
            "FirstName",
            "TeamName",
            "Position",
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
        Process the raw qualifying data and return a processed DataFrame.

        Args:
            df_raw (pd.DataFrame): The raw DataFrame containing qualifying data.
            year (int): The year of the session.
            round (int): The round number of the session.

        Returns:
            pd.DataFrame: The processed DataFrame with the following columns:
                - id_driver: The driver ID.
                - name_driver_last: The last name of the driver.
                - name_driver_first: The first name of the driver.
                - name_team: The name of the team.
                - session: The qualifying session (Q1, Q2, or Q3).
                - time: The qualifying time.
                - position: The qualifying position of the driver in the session.
        """

        self.df_processed = df_raw.melt(
            id_vars=["DriverId", "LastName", "FirstName", "TeamName", "Position"],
            value_vars=["Q1", "Q2", "Q3"],
            var_name="session",
            value_name="time",
        )

        self.df_processed.columns = self.df_processed.columns.str.lower()

        self.df_processed["year"] = year
        self.df_processed["round"] = round
        self.df_processed["originalposition"] = self.df_processed["position"]
        self.df_processed["position"] = self.df_processed.groupby("session")[
            "time"
        ].rank(method="min", ascending=True)
        self.df_processed["position"] = self.df_processed["position"].fillna(
            self.df_processed["originalposition"]
        )

        self.df_processed = self.df_processed.drop(columns=["originalposition"])

        self.df_processed.rename(
            columns={
                "driverid": "id_driver",
                "lastname": "name_driver_last",
                "firstname": "name_driver_first",
                "teamname": "name_team",
            },
            inplace=True,
        )

        return self.df_processed

    def __get_df_final(self, df_processed: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts the required columns from the processed DataFrame and returns a new DataFrame.

        Args:
            df_processed (pd.DataFrame): The processed DataFrame containing the F1 data.

        Returns:
            pd.DataFrame: A new DataFrame with the following columns:
                - id_driver: The ID of the driver.
                - name_driver_last: The last name of the driver.
                - name_driver_first: The first name of the driver.
                - name_team: The name of the team.
                - session: The session of the race.
                - position: The position of the driver in the race.
                - time: The time taken by the driver in the race.
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

    def get_df_quali(self, data_session: object, year: int, round: int) -> pd.DataFrame:
        """
        Retrieves the final DataFrame containing the qualifying session data.

        Args:
            data_session (object): The raw qualifying session data.
            year (int): The year of the session.
            round (int): The round number of the session.

        Returns:
            pd.DataFrame: A DataFrame containing the qualifying session data.
        """

        df_raw = self.__get_df_raw(data_session)
        df_processed = self.__get_df_processed(df_raw, year, round)
        df_final = self.__get_df_final(df_processed)

        return df_final
