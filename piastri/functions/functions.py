import fastf1 as ff1
import pandas as pd
import os

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from typing import Dict, List


def get_years(start: int, end: int) -> List[int]:
    """
    Get the list of years for which data exists.

    Args:
        start (int): The first year for which to retrieve data.
        end (int): The last year for which to retrieve data.

    Returns:
        List: A list of years.
    """

    years = list(range(start, end + 1))

    return years


def get_rounds(year: int) -> List[int]:
    """
    Get the list of round numbers for a given year.

    Args:
        year (int): The year for which to retrieve round numbers.

    Returns:
        list: A list of round numbers.
    """

    schedule = ff1.get_event_schedule(year)
    rounds_all = schedule.RoundNumber.to_list()
    rounds_official = [r for r in rounds_all if r > 0]

    return rounds_official


def get_df_quali_raw(year: int, round: int) -> pd.DataFrame:
    """
    Retrieve qualifying session data for a given year and round.

    Args:
        year (int): The year of the session.
        round (int): The round number of the session.

    Returns:
        pd.DataFrame: A DataFrame containing the qualifying session data.
    """

    session = ff1.get_session(year, round, "Q")
    session.load()

    df = session.results[
        ["Q1", "Q2", "Q3", "DriverId", "LastName", "FirstName", "TeamName", "Position"]
    ]

    return df


def get_df_quali_processed(df_raw: pd.DataFrame, year: int, round: int) -> pd.DataFrame:
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

    df = df_raw.melt(
        id_vars=["DriverId", "LastName", "FirstName", "TeamName", "Position"],
        value_vars=["Q1", "Q2", "Q3"],
        var_name="session",
        value_name="time",
    )

    df.columns = df.columns.str.lower()

    df["year"] = year
    df["round"] = round
    df["originalposition"] = df["position"]
    df["position"] = df.groupby("session")["time"].rank(method="min", ascending=True)
    df["position"] = df["position"].fillna(df["originalposition"])

    df = df.drop(columns=["originalposition"])

    df.rename(
        columns={
            "driverid": "id_driver",
            "lastname": "name_driver_last",
            "firstname": "name_driver_first",
            "teamname": "name_team",
        },
        inplace=True,
    )

    return df


def get_df_quali_final(df_processed: pd.DataFrame) -> pd.DataFrame:
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

    df = df_processed[
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

    return df


def get_df_race_raw(year: int, round: int) -> pd.DataFrame:
    """
    Retrieve race session data for a given year and round.

    Args:
        year (int): The year of the session.
        round (int): The round number of the session.

    Returns:
        pd.DataFrame: A DataFrame containing the race session data.
    """

    session = ff1.get_session(year, round, "R")
    session.load()

    df = session.results[
        [
            "DriverId",
            "LastName",
            "FirstName",
            "TeamName",
            "ClassifiedPosition",
            "Time",
        ]
    ]

    return df


def get_df_race_processed(df_raw: pd.DataFrame, year: int, round: int) -> pd.DataFrame:
    """
    Process the raw race data and return a processed DataFrame.

    Args:
        df_raw (pd.DataFrame): The raw race data DataFrame.
        year (int): The year of the session.
        round (int): The round number of the session.

    Returns:
        pd.DataFrame: The processed race data DataFrame.
    """

    df = df_raw.copy().reset_index(drop=True)

    df["year"] = year
    df["round"] = round
    df["session"] = "Race"

    df.columns = df.columns.str.lower()
    df.rename(
        columns={
            "classifiedposition": "position",
            "driverid": "id_driver",
            "lastname": "name_driver_last",
            "firstname": "name_driver_first",
            "teamname": "name_team",
        },
        inplace=True,
    )
    df.loc[1:, "time"] = df.loc[1:, "time"] + df.loc[0, "time"]

    return df


def get_df_race_final(df_processed: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame containing the final race data.

    Args:
        df_processed (pd.DataFrame): The processed DataFrame containing race data.

    Returns:
        pd.DataFrame: The DataFrame containing the final race data.
    """

    df = df_processed[
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

    return df


def get_df_event_raw(year: int, round: int) -> pd.DataFrame:
    """
    Retrieve event session data for a given year and round.

    Args:
        year (int): The year of the session.
        round (int): The round number of the session.

    Returns:
        pd.DataFrame: A DataFrame containing the event session data.
    """

    session = ff1.get_session(year, round, "R")
    session.load()

    df = session.event[["RoundNumber", "Location", "EventDate", "Country"]].to_frame()

    return df


def get_df_event_processed(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Process the raw event data and return a processed DataFrame.

    Args:
        df_raw (pd.DataFrame): The raw event data DataFrame.

    Returns:
        pd.DataFrame: The processed event data DataFrame.
    """

    df = df_raw.T.reset_index(drop=True)

    df.columns = df.columns.str.lower()
    df.rename(
        columns={
            "roundnumber": "round",
            "location": "circuit_name",
            "country": "circuit_country",
        },
        inplace=True,
    )
    df["year"] = df["eventdate"].dt.year
    df["round"] = df["round"].astype(int)

    return df


def get_df_event_final(df_processed: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame containing the final event data.

    Args:
        df_processed (pd.DataFrame): The processed DataFrame containing event data.

    Returns:
        pd.DataFrame: The DataFrame containing the final event data.
    """

    df = df_processed[["year", "round", "circuit_name", "circuit_country"]]

    return df


def get_df_sessions(df_quali: pd.DataFrame, df_race: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenates the given qualifying and race DataFrames into a single DataFrame.

    Args:
        df_quali (pd.DataFrame): The DataFrame containing qualifying data.
        df_race (pd.DataFrame): The DataFrame containing race data.

    Returns:
        pd.DataFrame: The concatenated DataFrame containing both qualifying and race data.
    """

    df = pd.concat([df_quali, df_race], ignore_index=True)

    return df


def get_df_denormalized(
    df_sessions: pd.DataFrame, df_event: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge the sessions DataFrame with the event DataFrame based on the year and round columns.

    Args:
        df_sessions (pd.DataFrame): The sessions DataFrame.
        df_event (pd.DataFrame): The event DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing denormalized data for sessions and event.
    """

    df_denormalized = df_event.merge(df_sessions, on=["year", "round"], how="outer")

    return df_denormalized


def get_df_events(df_event: pd.DataFrame) -> pd.DataFrame:
    """
    Get a DataFrame isolating normalized event data.

    Args:
        df_event (pd.DataFrame): The input DataFrame containing event data.

    Returns:
        pd.DataFrame: Normalized DataFrame with columns 'year', 'round', and 'circuit_name'.
    """

    df = df_event[["year", "round", "circuit_name"]].reset_index(drop=True)

    return df


def get_df_drivers(df_sessions: pd.DataFrame) -> pd.DataFrame:
    """
    Get a DataFrame isolating normalized driver data.

    Args:
        df_event (pd.DataFrame): The input DataFrame containing driver data.

    Returns:
        pd.DataFrame: Normalized DataFrame with columns.
            'id_driver', 'name_driver_last', and 'name_driver_first'.
    """

    df = (
        df_sessions[["id_driver", "name_driver_last", "name_driver_first"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return df


def get_df_teams(df_sessions: pd.DataFrame) -> pd.DataFrame:
    """
    Get a DataFrame isolating normalized team data.

    Args:
        df_event (pd.DataFrame): The input DataFrame containing team data.

    Returns:
        pd.DataFrame: Normalized DataFrame with columns.
            'name_team', 'year', and 'id_driver'.
    """

    df = (
        df_sessions[["name_team", "year", "id_driver"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return df


def get_df_circuits(df_event: pd.DataFrame) -> pd.DataFrame:
    """
    Get a DataFrame isolating normalized circuit data.

    Args:
        df_event (pd.DataFrame): The input DataFrame containing circuit data.

    Returns:
        pd.DataFrame: Normalized DataFrame with columns.
            'circuit_name' and 'circuit_country'.
    """

    df = df_event[["circuit_name", "circuit_country"]].reset_index(drop=True)

    return df


def get_df_results(df_sessions: pd.DataFrame) -> pd.DataFrame:
    """
    Get a DataFrame isolating normalized result data.

    Args:
        df_event (pd.DataFrame): The input DataFrame containing result data.

    Returns:
        pd.DataFrame: Normalized DataFrame with columns.
            'year', 'round', 'id_driver', 'name_team', 'session', 'position' and 'time'.
    """

    df = df_sessions[
        ["year", "round", "id_driver", "name_team", "session", "position", "time"]
    ].reset_index(drop=True)

    return df


def get_env_var(filename: str) -> None:
    """
    Reads environment variable key-value pairs from a file and sets them in the os.environ dictionary.

    Args:
        filename (str): The name of the file containing the environment variable key-value pairs.

    Returns:
        None.
    """

    with open(filename) as file:
        for line in file:
            if line.strip():
                key, value = line.strip().split("=", 1)
                os.environ[key] = value


def write_df_postgres(
    user: str,
    password: str,
    database: str,
    host: str,
    port: str,
    df: pd.DataFrame,
    table: str,
    keys: List[str],
) -> None:
    """
    Write a DataFrame to a PostgreSQL table.

    Args:
        user (str): The username for the database connection.
        password (str): The password for the database connection.
        database (str): The name of the database.
        host (str): The host address of the database.
        port (str): The port number of the database.
        df (pd.DataFrame): The DataFrame to be written to the database.
        table (str): The target table for the DataFrame.
        keys (List[str]): A list of primary key columns for the target table.

    Returns:
        None.
    """

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

    data = df.to_dict("records")

    stmt = insert(f"sessions.{table}").values(data)
    stmt = stmt.on_conflict_do_nothing(index_elements={keys})

    with engine.begin() as connection:
        connection.execute(stmt)
