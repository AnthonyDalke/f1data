import fastf1 as ff1
import os
import pandas as pd


# def get_years(start, end):
#     """
#     Get the list of years for which data exists.

#     Parameters:
#     start (int): The first year for which to retrieve data.
#     end (int): The last year for which to retrieve data.

#     Returns:
#     list: A list of years.
#     """

#     years = list(range(start, end + 1))

#     return years


# def get_rounds(year):
#     """
#     Get the list of round numbers for a given year.

#     Parameters:
#     year (int): The year for which to retrieve round numbers.

#     Returns:
#     list: A list of round numbers.
#     """

#     schedule = ff1.get_event_schedule(1994)
#     rounds = schedule.RoundNumber.to_list()

#     return rounds


def get_df_raw_quali(year: int, round: int) -> pd.DataFrame:
    """
    Retrieve qualifying session data for a given year and round.

    Parameters:
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


def get_df_processed_quali(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Process the raw qualifying data and return a processed DataFrame.

    Args:
        df_raw (pd.DataFrame): The raw DataFrame containing qualifying data.

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


def get_df_final_quali(df_processed: pd.DataFrame) -> pd.DataFrame:
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


def get_df_raw_race(year: int, round: int) -> pd.DataFrame:
    """
    Retrieve race session data for a given year and round.

    Parameters:
    year (int): The year of the session.
    round (int): The round number of the session.

    Returns:
    pd.DataFrame: A DataFrame containing the race session data.
    """

    session = ff1.get_session(1950, 1, "R")
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


def get_df_processed_race(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Process the raw race data and return a processed DataFrame.

    Parameters:
    - df_raw (pd.DataFrame): The raw race data DataFrame.

    Returns:
    - pd.DataFrame: The processed race data DataFrame.
    """

    df = df_raw.copy().reset_index(drop=True)

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


def get_df_final_race(df_processed: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame containing the final race data.

    Args:
        df_processed (pd.DataFrame): The processed DataFrame containing race data.

    Returns:
        pd.DataFrame: The DataFrame containing the final race data.
    """

    df = df_processed[
        [
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


def main():
    year_start = os.environ["year_start"]
    year_end = os.environ["year_end"]

    list_years = get_years(year_start, year_end)

    for year in list_years:
        list_rounds = get_rounds(year)


if __name__ == "__main__":
    main()
