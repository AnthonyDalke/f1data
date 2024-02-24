import os
import pandas as pd
import time

from functions.functions import (
    get_years,
    get_rounds,
    get_df_quali_raw,
    get_df_quali_processed,
    get_df_quali_final,
    get_df_race_raw,
    get_df_race_processed,
    get_df_race_final,
    get_df_event_raw,
    get_df_event_processed,
    get_df_event_final,
    get_df_sessions,
    get_df_denormalized,
    get_df_events,
    get_df_drivers,
    get_df_teams,
    get_df_circuits,
    get_df_results,
    get_env_var,
    write_df_postgres,
)

DB_NAME = os.environ["DB_NAME"]


def main():
    get_env_var(".env")

    db_name = os.environ["POSTGRES_DB"]
    db_user = os.environ["POSTGRES_USER"]
    db_password = os.environ["POSTGRES_PASSWORD"]
    db_host = "localhost"
    db_port = "5432"

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

    df_sessions_all = get_df_sessions(df_quali_all, df_race_all)
    df_denormalized = get_df_denormalized(df_sessions_all, df_event_all)
    df_events = get_df_events(df_event_all)
    df_drivers = get_df_drivers(df_sessions_all)
    df_teams = get_df_teams(df_sessions_all)
    df_circuits = get_df_circuits(df_event_all)
    df_results = get_df_results(df_sessions_all)

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
            "table": "denormalized",
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


if __name__ == "__main__":
    main()
