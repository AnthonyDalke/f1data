import pandas as pd


class DataEvent:
    def __init__(self):
        self.df_event_raw = None
        self.df_event_processed = None
        self.df_event_final = None

    def __get_df_raw(self, data_session: object) -> pd.DataFrame:
        """
        Retrieve event session data for a given year and round.

        Args:
            data_session (object): Raw session data.

        Returns:
            pd.DataFrame: A DataFrame with the relevant columns from the event data.
        """

        self.df_raw = data_session.event[
            ["RoundNumber", "Location", "EventDate", "Country"]
        ].to_frame()

        return self.df_raw

    def __get_df_processed(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Process the raw event data and return a processed DataFrame.

        Args:
            df_raw (pd.DataFrame): The raw event data DataFrame.

        Returns:
            pd.DataFrame: The processed event data DataFrame.
        """

        self.df_processed = df_raw.T.reset_index(drop=True)

        self.df_processed.columns = self.df_processed.columns.str.lower()
        self.df_processed.rename(
            columns={
                "roundnumber": "round",
                "location": "circuit_name",
                "country": "circuit_country",
            },
            inplace=True,
        )

        self.df_processed["eventdate"] = pd.to_datetime(self.df_processed["eventdate"])
        self.df_processed["year"] = self.df_processed["eventdate"].dt.year
        self.df_processed["round"] = self.df_processed["round"].astype(int)

        return self.df_processed

    def __get_df_final(self, df_processed: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a DataFrame containing the final event data.

        Args:
            df_processed (pd.DataFrame): The processed DataFrame containing event data.

        Returns:
            pd.DataFrame: The DataFrame containing the final event data.
        """

        self.df_final = df_processed[
            ["year", "round", "circuit_name", "circuit_country"]
        ]

        return self.df_final

    def get_df_event(self, data_session: object) -> pd.DataFrame:
        """
        Retrieve and process event session data.

        Args:
            data_session (object): Raw session data.

        Returns:
            pd.DataFrame: The final event data DataFrame.
        """

        df_raw = self.__get_df_raw(data_session)
        df_processed = self.__get_df_processed(df_raw)
        df_final = self.__get_df_final(df_processed)

        return df_final
