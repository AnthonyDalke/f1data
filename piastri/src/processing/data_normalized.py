import pandas as pd


class DataNormalized:
    def __init__(self):
        self.df_events = None
        self.df_drivers = None
        self.df_teams = None
        self.df_circuits = None
        self.df_results = None

    def get_df_events(self, df_event: pd.DataFrame) -> pd.DataFrame:
        """
        Get a DataFrame isolating normalized event data.

        Args:
            df_event (pd.DataFrame): The input DataFrame containing event data.

        Returns:
            pd.DataFrame: Normalized DataFrame with columns 'year', 'round', and 'name_circuit'.
        """

        self.df_events = df_event[["year", "round", "name_circuit"]].reset_index(
            drop=True
        )

        return self.df_events

    def get_df_drivers(self, df_sessions: pd.DataFrame) -> pd.DataFrame:
        """
        Get a DataFrame isolating normalized driver data.

        Args:
            df_driver (pd.DataFrame): The input DataFrame containing driver data.

        Returns:
            pd.DataFrame: Normalized DataFrame with columns.
                'id_driver', 'name_driver_last', and 'name_driver_first'.
        """

        self.df_drivers = (
            df_sessions[["id_driver", "name_driver_last", "name_driver_first"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        return self.df_drivers

    def get_df_teams(self, df_sessions: pd.DataFrame) -> pd.DataFrame:
        """
        Get a DataFrame isolating normalized team data.

        Args:
            df_event (pd.DataFrame): The input DataFrame containing team data.

        Returns:
            pd.DataFrame: Normalized DataFrame with columns.
                'name_team', 'year', and 'id_driver'.
        """

        self.df_teams = (
            df_sessions[["name_team", "year", "id_driver"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        return self.df_teams

    def get_df_circuits(self, df_event: pd.DataFrame) -> pd.DataFrame:
        """
        Get a DataFrame isolating normalized circuit data.

        Args:
            df_event (pd.DataFrame): The input DataFrame containing circuit data.

        Returns:
            pd.DataFrame: Normalized DataFrame with columns.
                'name_circuit' and 'country_circuit'.
        """

        self.df_circuits = df_event[["name_circuit", "country_circuit"]].reset_index(
            drop=True
        )

        return self.df_circuits

    def get_df_results(self, df_sessions: pd.DataFrame) -> pd.DataFrame:
        """
        Get a DataFrame isolating normalized result data.

        Args:
            df_event (pd.DataFrame): The input DataFrame containing result data.

        Returns:
            pd.DataFrame: Normalized DataFrame with columns.
                'year', 'round', 'id_driver', 'name_team', 'session', 'position' and 'time'.
        """

        self.df_results = df_sessions[
            ["year", "round", "id_driver", "name_team", "session", "position", "time"]
        ].reset_index(drop=True)

        return self.df_results
