import json
import logging
import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

import fastf1 as ff1
import pandas as pd

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger object.
    """

    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


def get_years(start: int, end: int) -> List[int]:
    """
    Get the list of years for which data exists.

    Args:
        start (int): The first year for which to retrieve data.
        end (int): The last year for which to retrieve data.

    Returns:
        List: A list of years.
    """

    return list(range(start, end + 1))


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
    return [r for r in rounds_all if r > 0]


def get_data_session(year: str, round: str, session: str) -> None:
    """
    Retrieve session data for a given year, round, and session.

    Args:
        year (str): The year of the session.
        round (str): The round number of the session.
        session (str): The session type (P, Q, R).

    Returns:
        None.
    """

    session = ff1.get_session(year, round, session)
    session.load()

    return session


def get_df_sessions(df_quali: pd.DataFrame, df_race: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenates the given qualifying and race DataFrames into a single DataFrame.

    Args:
        df_quali (pd.DataFrame): The DataFrame containing qualifying data.
        df_race (pd.DataFrame): The DataFrame containing race data.

    Returns:
        pd.DataFrame: The concatenated DataFrame containing both qualifying and race data.
    """

    return pd.concat([df_quali, df_race], ignore_index=True)


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

    return df_event.merge(df_sessions, on=["year", "round"], how="outer")


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


def set_env_var():
    """
    Retrieves and returns environment variables related to database configuration and other settings.

    Environment Variables:
        - POSTGRES_DB: Name of the PostgreSQL database.
        - POSTGRES_USER: Username for the PostgreSQL database.
        - POSTGRES_PASSWORD: Password for the PostgreSQL database.
        - POSTGRES_HOST: Host address of the PostgreSQL database.
        - POSTGRES_PORT: Port number of the PostgreSQL database.
        - YEAR_START: Starting year for some process (converted to int).
        - YEAR_END: Ending year for some process (converted to int).
        - SCHEMA_NAME: Name of the schema in the PostgreSQL database.
        - EMAIL_PW: Password for email.

    Returns:
        tuple: A tuple containing the following elements:
            - db_name (str): Name of the PostgreSQL database.
            - db_user (str): Username for the PostgreSQL database.
            - db_password (str): Password for the PostgreSQL database.
            - db_host (str): Host address of the PostgreSQL database.
            - db_port (str): Port number of the PostgreSQL database.
            - year_start (int): Starting year for some process.
            - year_end (int): Ending year for some process.
            - schema (str): Name of the schema in the PostgreSQL database.
            - pw (str): Password for email.
    """

    db_name = os.environ["POSTGRES_DB"]
    db_user = os.environ["POSTGRES_USER"]
    db_password = os.environ["POSTGRES_PASSWORD"]
    db_host = os.environ["POSTGRES_HOST"]
    db_port = os.environ["POSTGRES_PORT"]

    year_start = int(os.environ["YEAR_START"])
    year_end = int(os.environ["YEAR_END"])

    schema = os.environ["SCHEMA_NAME"]

    pw = os.environ["EMAIL_PW"]

    return (
        db_name,
        db_user,
        db_password,
        db_host,
        db_port,
        year_start,
        year_end,
        schema,
        pw,
    )


def write_df_postgres(
    user: str,
    password: str,
    database: str,
    host: str,
    port: str,
    df: pd.DataFrame,
    schema: str,
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
        schema (str): The schema for the target table.
        table (str): The target table for the DataFrame.
        keys (List[str]): A list of primary key columns for the target table.

    Returns:
        None.
    """

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

    metadata = MetaData()
    obj_table = Table(table, metadata, autoload_with=engine, schema=schema)

    data = df.to_dict("records")

    stmt = insert(obj_table).values(data)
    stmt = stmt.on_conflict_do_nothing(index_elements=keys)

    with engine.begin() as connection:
        connection.execute(stmt)


def email_missing_data(
    session: Dict[str, List],
    quali: Dict[str, List],
    race: Dict[str, List],
    event: Dict[str, List],
    pw: str,
    logger: logging.Logger,
) -> None:
    """
    Email the years and rounds with missing data, for triage.

    Args:
        session (Dict[List]): A dictionary containing missing session data.
        quali (Dict[List]): A dictionary containing missing qualifying data.
        race (Dict[List]): A dictionary containing missing race data.
        event (Dict[List]): A dictionary containing missing event data.
    """

    session_str = json.dumps(session, indent=4)
    quali_str = json.dumps(quali, indent=4)
    race_str = json.dumps(race, indent=4)
    event_str = json.dumps(event, indent=4)

    sender_email = "anthony.dalke@gmail.com"
    receiver_email = "anthony.dalke@gmail.com"
    subject = "Missing Data for F1 ETL Run"
    body = (
        f"Session Missing:\n{session_str}\n\n"
        f"Quali Missing:\n{quali_str}\n\n"
        f"Race Missing:\n{race_str}\n\n"
        f"Event Missing:\n{event_str}"
    )

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "anthony.dalke@gmail.com"
    smtp_password = pw

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()

        logger.info("Emailed details of missing data.")
    except Exception as e:
        logger.error(f"Failed to email details of missing data due to error {e}.")
