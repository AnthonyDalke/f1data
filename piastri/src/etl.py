import fastf1 as ff1
import os
import pandas as pd
import time
from typing import List


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


def main():
    year_start = int(os.environ["year_start"])
    year_end = int(os.environ["year_end"])

    df_quali_all = []
    df_race_all = []
    df_event_all = []

    list_years = get_years(year_start, year_end)

    for year in list_years:
        print(f"year: {year}")
        list_rounds = get_rounds(year)

        for round in list_rounds:
            df_quali_raw = get_df_quali_raw(year, round)
            df_quali_processed = get_df_quali_processed(df_quali_raw, year, round)
            df_quali_final = get_df_quali_final(df_quali_processed)

            df_quali_all.append(df_quali_final)

            time.sleep(3)

            df_race_raw = get_df_race_raw(year, round)
            df_race_processed = get_df_race_processed(df_race_raw, year, round)
            df_race_final = get_df_race_final(df_race_processed)

            df_race_all.append(df_race_final)

            time.sleep(3)

            df_event_raw = get_df_event_raw(year, round)
            df_event_processed = get_df_event_processed(df_event_raw)
            df_event_final = get_df_event_final(df_event_processed)

            df_event_all.append(df_event_final)

            time.sleep(3)

    df_quali_all = pd.concat(df_quali_all, ignore_index=True)
    df_race_all = pd.concat(df_race_all, ignore_index=True)
    df_event_all = pd.concat(df_event_all, ignore_index=True)

    print(f"df_quali_all: {df_quali_all}")
    print(f"df_race_all: {df_race_all}")
    print(f"df_event_all: {df_event_all}")


if __name__ == "__main__":
    main()
