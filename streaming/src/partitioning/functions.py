from pyspark.sql import SparkSession

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
            spark_builder = spark_builder.master(value)
        else:
            spark_builder = spark_builder.config(key, value)

    return spark_builder.getOrCreate()
