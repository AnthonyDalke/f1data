import matplotlib.figure as fig
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyspark.sql import DataFrame, SparkSession

from spark_config import config_base, config_keys


def time_process(time_start: float, time_end: float, name_process: str) -> None:
    """
    Calculate the duration of a process and print it.

    Args:
        time_start: The start time of the process.
        time_end: The end time of the process.
        name_process: A descriptive name of the process.
    """

    duration = time_end - time_start
    print(f"Duration of {name_process} process: {duration:.2f} seconds")


def create_spark_session(test_setting: str, test_value: str) -> SparkSession:
    """
    Create a Spark session with dynamic configuration based on test parameters.

    Args:
        test_setting: Configuration setting to test. Must enter one of the following:
            'master', 'repartitioning', 'driver.memory', 'shuffle.partitions', or 'serializer'.
        test_value: Value to use for the configuration setting to test.

    Returns:
        Configured SparkSession
    """

    # Begin with base of Spark Session configuration
    spark_config = config_base[test_setting].copy()

    # Assemble rest of Spark Session configuration based on test parameters
    if test_setting == "serializer":
        is_kryo = test_value.lower() == "kryo"
        spark_config["spark.serializer"] = (
            "org.apache.spark.serializer.KryoSerializer"
            if is_kryo
            else "org.apache.spark.serializer.JavaSerializer"
        )
        spark_config["spark.kryo.registrationRequired"] = str(is_kryo).lower()
    else:
        spark_config[config_keys[test_setting]] = test_value

    # Define the Spark Session
    spark_builder = SparkSession.builder.appName(
        f"partitioning_{test_setting}_{test_value}"
    )

    # Add Spark Session configuration details to builder
    for key, value in spark_config.items():
        if key == "master":
            spark_builder = spark_builder.master(f"local[{value}]")
        else:
            spark_builder = spark_builder.config(key, value)

    return spark_builder.getOrCreate()


def get_partition_stats(df: DataFrame, sequencing: str) -> None:
    """
    Display partition statistics for a given DataFrame.

    Args:
        df: The DataFrame to analyze.
        sequencing: Indication of whether stats come from before or after repartitioning.
    """

    print(f"Count of partitions {sequencing} partitioning: {df.rdd.getNumPartitions()}")
    print(
        f"Partition sizes (rows) {sequencing} partitioning: {df.rdd.glom().map(len).collect()}"
    )


def plot_distributions(df: pd.DataFrame) -> fig.Figure:
    """
    Create simple distribution plots for each column in the dataframe.
    Handles numeric, categorical, boolean and datetime data types.
    """

    n_plots = len(df.columns)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols

    fig = plt.figure(figsize=(15, 4 * n_rows))

    for idx, col in enumerate(df.columns, 1):
        ax = plt.subplot(n_rows, n_cols, idx)
        dtype = df[col].dtype

        if dtype in ["float64", "int64"]:
            df[col].hist(bins=15, edgecolor="white", linewidth=0.5, ax=ax)
        elif dtype == "bool":
            df[col].value_counts().plot(kind="bar", ax=ax)
        elif dtype == "object":
            df[col].value_counts().head(10).plot(kind="bar", ax=ax)
        elif dtype == "datetime64[ns]":
            df[col].astype(np.int64).hist(
                bins=15, edgecolor="white", linewidth=0.5, ax=ax
            )
            plt.xlabel("Date", fontsize=9)
        elif dtype == "timedelta64[ns]":
            df[col].dt.total_seconds().hist(
                bins=15, edgecolor="white", linewidth=0.5, ax=ax
            )
            plt.xlabel("Duration (s)", fontsize=9)

        plt.title(col, fontsize=11, pad=8)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

    plt.tight_layout(pad=2.0, h_pad=3.0, w_pad=2.0)

    return fig
