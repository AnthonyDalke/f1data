import os
import time

import fastf1 as ff1
import matplotlib.pyplot as plt
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.functions import count

from functions import create_spark_session, time_process
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
    session_name: str = input(
        "Enter the abbrevation of the session name to load (e.g., 'Q' or 'R'): "
    )

    load_start: float = time.time()

    session_object = ff1.get_session(session_year, session_location, session_name)
    session_object.load()

    load_end: float = time.time()
    time_process(load_start, load_end, "session data load")

    # Fetch telemetry data for all drivers from session
    print(
        f"Fetching telemetry data for full driver list: {len(session_object.drivers)}"
    )

    telemetry_data = []
    for driver in session_object.drivers:
        try:
            driver_data = session_object.laps.pick_drivers(driver).get_telemetry()
            if not driver_data.empty:
                driver_data["Driver"] = driver
                driver_data["SessionKey"] = (
                    f"{session_object.event.EventName} {session_object.name}"
                )
                telemetry_data.append(driver_data)
        except Exception as e:
            print(f"Error while loading data for driver {driver}: {e}")

    # Concatenate all driver telemetry into a single dataframe
    try:
        combined_telemetry = pd.concat(telemetry_data, ignore_index=True)
        print(f"Records in combined telemetry data: {len(combined_telemetry)}")
        print(f"Preview of combined telemetry data: {combined_telemetry.head()}")
    except Exception as e:
        print(f"Error while concatenating driver telemetry data: {e}.")
        combined_telemetry = pd.DataFrame()

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

    if test_setting == "repartitioning":
        # Generate histograms to assess for skew
        combined_telemetry.hist(figsize=(12, 8))
        plt.tight_layout()
        plt.show()

        combined_telemetry["Driver"].value_counts().plot(
            kind="bar", figsize=(10, 4), title="Driver Distribution"
        )
        plt.ylabel("Count")
        plt.show()

    spark_session = create_spark_session(test_setting, test_value)
    df_base: DataFrame = spark_session.createDataFrame(combined_telemetry)

    time_start: float = time.time()

    process_monitor = ProcessMonitor()
    process_monitor.start()

    df_repartitioned: DataFrame = df_base.repartition(6, "SessionTime").persist()
    df_agg: DataFrame = df_repartitioned.groupBy("Driver").agg(
        count("Speed").alias("SpeedCount")
    )
    df_agg.write.mode("overwrite").parquet(f"{test_setting}_{test_value}")

    process_monitor.stop()

    time_end: float = time.time()
    time_process(time_start, time_end, test_setting)

    input(f"Press Enter to stop Spark session...")
    spark_session.stop()


if __name__ == "__main__":
    main()
