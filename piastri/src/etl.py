import logging
import os
import pandas as pd
import time
from typing import List, Tuple

from functions.functions import (
    get_years,
    get_rounds,
    get_data_session,
    get_df_sessions,
    get_df_denormalized,
    get_env_var,
    set_env_var,
    write_df_postgres,
)

from .processing.data_quali import DataQuali
from .processing.data_race import DataRace
from .processing.data_event import DataEvent
from .processing.data_normalized import DataNormalized

logger = logging.getLogger("piastri")
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def extract_transform_history(
    list_years: List[int],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Extracts and transforms historical data for qualifying, race, and event sessions for multiple years and rounds.
    Args:
        list_years (List[int]): A list of years to extract and transform.
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: A tuple containing three pandas DataFrames:
            - df_quali_all: DataFrame containing qualifying session data for all years and rounds.
            - df_race_all: DataFrame containing race session data for all years and rounds.
            - df_event_all: DataFrame containing event data for all years and rounds.
    """

    df_quali_all = []
    df_race_all = []
    df_event_all = []

    for year in list_years:
        logger.info(f"year: {year}")
        list_rounds = get_rounds(year)

        for round in list_rounds:
            data_session_quali = get_data_session(year, round, "Q")
            data_session_race = get_data_session(year, round, "R")
            logger.info(
                f"Retrieved qualifying and race session data for round {round} of {year}."
            )

            instance_quali = DataQuali()
            df_quali = instance_quali.get_df_quali(data_session_quali, year, round)
            df_quali_all.append(df_quali)
            logger.info(f"Retrieved qualifying dataframe for round {round} of {year}.")

            time.sleep(3)

            instance_race = DataRace()
            df_race = instance_race.get_df_race(data_session_race, year, round)
            df_race_all.append(df_race)
            logger.info(f"Retrieved race dataframe for round {round} of {year}.")

            time.sleep(3)

            instance_event = DataEvent()
            df_event = instance_event.get_df_event(data_session_race)
            df_event_all.append(df_event)
            logger.info(f"Retrieved event dataframe for round {round} of {year}.")

            time.sleep(3)

    df_quali_all = pd.concat(df_quali_all, ignore_index=True)
    df_race_all = pd.concat(df_race_all, ignore_index=True)
    df_event_all = pd.concat(df_event_all, ignore_index=True)

    return df_quali_all, df_race_all, df_event_all


def extract_transform_tables(
    df_quali_all: pd.DataFrame, df_race_all: pd.DataFrame, df_event_all: pd.DataFrame
) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    """
    Extracts and transforms data from multiple dataframes to generate denormalized tables.
    Args:
        df_quali_all (pd.DataFrame): The dataframe containing qualifying data.
        df_race_all (pd.DataFrame): The dataframe containing race data.
        df_event_all (pd.DataFrame): The dataframe containing event data.
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
            A tuple of dataframes representing the denormalized tables:
            - df_denormalized: The dataframe for the denormalized table.
            - df_events: The dataframe containing normalized event data.
            - df_drivers: The dataframe containing normalized driver data.
            - df_teams: The dataframe containing normalized team data.
            - df_circuits: The dataframe containing normalized circuit data.
            - df_results: The dataframe containing normalized result data.
    """

    df_sessions_all = get_df_sessions(df_quali_all, df_race_all)
    df_denormalized = get_df_denormalized(df_sessions_all, df_event_all)
    df_events = DataNormalized.get_df_events(df_event_all)
    df_drivers = DataNormalized.get_df_drivers(df_sessions_all)
    df_teams = DataNormalized.get_df_teams(df_sessions_all)
    df_circuits = DataNormalized.get_df_circuits(df_event_all)
    df_results = DataNormalized.get_df_results(df_sessions_all)

    return df_denormalized, df_events, df_drivers, df_teams, df_circuits, df_results


def load_postgres(
    db_user: str,
    db_password: str,
    db_name: str,
    db_host: str,
    db_port: str,
    df_denormalized: pd.DataFrame,
    df_events: pd.DataFrame,
    df_drivers: pd.DataFrame,
    df_teams: pd.DataFrame,
    df_circuits: pd.DataFrame,
    df_results: pd.DataFrame,
) -> None:
    """
    Loads the given DataFrames into corresponding tables in Postgres.

    Args:
        db_user (str): The username for the PostgreSQL database.
        db_password (str): The password for the PostgreSQL database.
        db_name (str): The name of the PostgreSQL database.
        db_host (str): The host address of the PostgreSQL database.
        db_port (str): The port number of the PostgreSQL database.
        df_denormalized (pd.DataFrame): The DataFrame containing denormalized data.
        df_events (pd.DataFrame): The DataFrame containing event data.
        df_drivers (pd.DataFrame): The DataFrame containing driver data.
        df_teams (pd.DataFrame): The DataFrame containing team data.
        df_circuits (pd.DataFrame): The DataFrame containing circuit data.
        df_results (pd.DataFrame): The DataFrame containing result data.

    Returns:
        None
    """

    dict_df = {
        "df_denormalized": df_denormalized,
        "df_events": df_events,
        "df_drivers": df_drivers,
        "df_teams": df_teams,
        "df_circuits": df_circuits,
        "df_results": df_results,
    }

    dict_db = {
        "df_denormalized": {
            "table": "events_denormalized",
            "primary_keys": ["year", "round", "id_driver", "session"],
        },
        "df_events": {"table": "events", "primary_keys": ["year", "round"]},
        "df_drivers": {"table": "drivers", "primary_keys": ["id_driver"]},
        "df_teams": {"table": "teams", "primary_keys": ["name_team", "year"]},
        "df_circuits": {"table": "circuits", "primary_keys": ["circuit_name"]},
        "df_results": {
            "table": "results",
            "primary_keys": ["year", "round", "id_driver", "session"],
        },
    }

    for df_name, df in dict_df.items():
        table_name = dict_db[df_name]["table"]
        primary_keys = dict_db[df_name]["primary_keys"]
        write_df_postgres(
            db_user,
            db_password,
            db_name,
            db_host,
            db_port,
            df,
            table_name,
            primary_keys,
        )

    return None


def main():
    """
    Main function for ETL process.

    This function performs the following steps:
    1. Retrieves environment variables from the ".env" file.
    2. Sets environment variables for database connection.
    3. Retrieves a list of years based on the start and end year provided.
    4. Extracts and transforms historical data for the specified years.
    5. Extracts and transforms historical data to load in Postgres tables.
    6. Loads the transformed data into a Postgres.

    Parameters:
    None

    Returns:
    None
    """

    get_env_var(".env")

    db_name, db_user, db_password, db_host, db_port, year_start, year_end = (
        set_env_var()
    )

    list_years = get_years(year_start, year_end)

    df_quali_all, df_race_all, df_event_all = extract_transform_history(list_years)

    df_denormalized, df_events, df_drivers, df_teams, df_circuits, df_results = (
        extract_transform_tables(df_quali_all, df_race_all, df_event_all)
    )

    load_postgres(
        db_user,
        db_password,
        db_name,
        db_host,
        db_port,
        df_denormalized,
        df_events,
        df_drivers,
        df_teams,
        df_circuits,
        df_results,
    )


if __name__ == "__main__":
    main()
