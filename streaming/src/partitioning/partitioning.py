# Set up environment variables for Java, required by PySpark
import os

os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@17"
os.environ["PATH"] = "/opt/homebrew/opt/openjdk@17/bin:" + os.environ["PATH"]


# Import necessary libraries
import time
from datetime import datetime
from typing import Dict

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option("display.max_columns", None)
import psutil
import fastf1 as ff1
from pyspark.sql import SparkSession
from pyspark.sql.functions import count

from spark_config import config_base, config_keys


def time_process(time_start: float, time_end: float, name_process: str) -> None:
    duration = time_end - time_start
    print(f"Duration of {name_process} process: {duration} seconds")


def create_spark_session(test_setting: str, test_value: str) -> SparkSession:
    """
    Create a Spark session with dynamic configuration based on test parameters.

    Args:
        test_setting: Configuration setting to test. Must enter of the following:
            'master', 'repartitioning', 'driver.memory', 'shuffle.partitions', or 'serializer'.
        test_value: Value to use for the configuration setting to test.

    Returns:
        Configured SparkSession
    """

    # Begin with base of Spark Session configuration
    spark_config = config_base[test_setting].copy()

    # Assemble rest of Spark Session configuration based on test parameters
    if test_setting == "serializer":
        if test_value.lower() == "kyro":
            spark_config["spark.serializer"] = (
                "org.apache.spark.serializer.KyroSerializer"
            )
            spark_config["spark.kyro.registrationRequired"] = "true"
        else:
            spark_config["spark.serializer"] = (
                "org.apache.spark.serializer.JavaSerializer"
            )
            spark_config["spark.kyro.registrationRequired"] = "false"
    else:
        spark_config[config_keys[test_setting]] = test_value

    # Define the Spark Session
    spark_builder = SparkSession.builder.appName(
        f"partitioning_{test_setting}_{test_value}"
    )

    # Add Spark Sesssion configuration details to builder
    for key, value in spark_config.items():
        if key == "master":
            spark_builder = spark_builder.master(value)
        else:
            spark_builder = spark_builder.config(key, value)

    return spark_builder.getOrCreate()


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

    # Generate histograms to assess for skew
    combined_telemetry.hist(figsize=(12, 8))
    plt.tight_layout()
    plt.show()

    combined_telemetry["Driver"].value_counts().plot(
        kind="bar", figsize=(10, 4), title="Driver Distribution"
    )
    plt.ylabel("Count")
    plt.show()

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
            f"Enter the value to test with the {test_setting} Spark Session configuration setting."
        )
    )
    print(
        f"Testing Spark Session configuration setting {test_setting} with a value of {test_value}."
    )

    spark_session = create_spark_session(test_setting, test_value)
    input(f"Press Enter to stop Spark session...")
    spark_session.stop()


if __name__ == "__main__":
    main()
