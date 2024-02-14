import os
import pandas as pd
import time

from functions import (
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
    get_env_var,
    run_sql_script,
)

DB_NAME = os.environ["DB_NAME"]


def main():
    get_env_var(".env")

    db_name = os.environ["POSTGRES_DB"]
    db_user = os.environ["POSTGRES_USER"]
    db_password = os.environ["POSTGRES_PASSWORD"]
    db_host = "localhost"
    db_port = "5432"

    sql_scripts = [
        "01_create_schema.sql",
        "02_create_tables.sql",
        "03_create_indexes.sql",
    ]

    run_sql_script(db_name, db_user, db_password, db_host, db_port, sql_scripts)

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

    df_sessions = get_df_sessions(df_quali_all, df_race_all)

    df_denormalized = get_df_denormalized(df_sessions, df_event_all)


if __name__ == "__main__":
    main()
