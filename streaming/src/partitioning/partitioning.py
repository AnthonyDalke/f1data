import os
import time

import fastf1 as ff1
import matplotlib.pyplot as plt
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.functions import count

from functions import (
    create_spark_session,
    get_partition_stats,
    plot_distributions,
    time_process,
)
from ProcessMonitor import ProcessMonitor
from spark_config import config_base

# Set up environment variables for Java, required by PySpark
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@17"
os.environ["PATH"] = "/opt/homebrew/opt/openjdk@17/bin:" + os.environ["PATH"]

# Configure pandas to display all DataFrame columns
pd.set_option("display.max_columns", None)


def main():
    # Load data for single session
    session_year: int = int(
        input("Enter the year of the session to load (e.g., 2025): ")
    )
    session_location: str = input(
        "Enter the location of the session to load (e.g., 'Monaco'): "
    )

    load_start: float = time.time()

    telemetry_data = []

    for session in ["FP1", "FP2", "FP3", "Q", "R"]:
        try:
            session_object = ff1.get_session(session_year, session_location, session)
            session_object.load()

            # Fetch telemetry data for all drivers from session
            print(f"Fetching telemetry data for {len(session_object.drivers)} drivers.")

            for driver in session_object.drivers:
                try:
                    driver_data = session_object.laps.pick_drivers(
                        driver
                    ).get_telemetry()
                    if not driver_data.empty:
                        driver_data["Driver"] = driver
                        driver_data["SessionKey"] = (
                            f"{session_object.event.EventName} {session_object.name}"
                        )
                        telemetry_data.append(driver_data)
                except Exception as e:
                    print(f"Error while loading data for driver {driver}: {e}")
        except Exception as e:
            print(f"Error while loading session {session}: {e}")

    # Concatenate all driver telemetry into a single dataframe
    try:
        combined_telemetry = pd.concat(telemetry_data, ignore_index=True)
        print(f"Records in combined telemetry data: {len(combined_telemetry)}")
    except Exception as e:
        print(f"Error while concatenating driver telemetry data: {e}.")
        combined_telemetry = pd.DataFrame()

    load_end: float = time.time()
    time_process(load_start, load_end, "session data load")

    fig = plot_distributions(combined_telemetry)
    plt.show()

    repartition_column: str = input(
        "Enter the column name to use for repartitioning (e.g., SessionTime)"
    )

    stop_command: str | None = None

    while stop_command != "stop":
        while True:
            test_setting: str = input(
                "Enter one of the following case-sensitive Spark Session configuration settings to test: 'master', 'repartitioning', 'driver.memory', 'shuffle.partitions', or 'serializer': "
            )
            if test_setting in config_base:
                break
            print(
                f"Invalid Spark Session configuration setting entered. Enter one of the following case-sensitive Spark Session configuration settings to test: 'master', 'repartitioning', 'driver.memory', 'shuffle.partitions', or 'serializer': "
            )
        test_value: str = str(
            input(
                f"Enter the value to test with the {test_setting} Spark Session configuration setting: "
            )
        )
        print(
            f"Testing Spark Session configuration setting {test_setting} with a value of {test_value}."
        )

        spark_session = create_spark_session(test_setting, test_value)
        df_base: DataFrame = spark_session.createDataFrame(combined_telemetry)

        time_start: float = time.time()

        process_monitor = ProcessMonitor()
        process_monitor.start()

        get_partition_stats(df_base, "before")

        df_repartitioned: DataFrame = df_base.repartition(
            6, repartition_column
        ).persist()
        get_partition_stats(df_repartitioned, "after")

        df_agg: DataFrame = df_repartitioned.groupBy("Driver").agg(
            count("Speed").alias("SpeedCount")
        )
        df_agg.write.mode("overwrite").parquet(f"{test_setting}_{test_value}")

        process_monitor.stop()

        time_end: float = time.time()
        time_process(time_start, time_end, test_setting)

        input(f"Press Enter to stop Spark session...")
        spark_session.stop()

        stop_command = str.lower(
            input(f"Enter 'stop' to end the program or anything else to continue: ")
        )


if __name__ == "__main__":
    main()
