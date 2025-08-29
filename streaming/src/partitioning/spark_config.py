config_base: dict[str, dict[str, str]] = {
    "master": {
        "spark.driver.memory": "6g",
        "spark.sql.shuffle.partitions": "6",
        "spark.serializer": "org.apache.spark.serializer.JavaSerializer",
        "spark.ui.port": "4040",
    },
    "repartitioning": {
        "local": "[6]",
        "spark.driver.memory": "6g",
        "spark.sql.shuffle.partitions": "6",
        "spark.serializer": "org.apache.spark.serializer.JavaSerializer",
        "spark.ui.port": "4040",
    },
    "driver.memory": {
        "local": "[6]",
        "spark.sql.shuffle.partitions": "6",
        "spark.serializer": "org.apache.spark.serializer.JavaSerializer",
        "spark.ui.port": "4040",
    },
    "shuffle.partitions": {
        "local": "[6]",
        "spark.driver.memory": "6g",
        "spark.serializer": "org.apache.spark.serializer.JavaSerializer",
        "spark.ui.port": "4040",
    },
    "serializer": {
        "local": "[6]",
        "spark.driver.memory": "6g",
        "spark.sql.shuffle.partitions": "6",
        "spark.ui.port": "4040",
    },
}

config_keys: dict[str, str] = {
    "master": "local",
    "driver.memory": "spark.driver.memory",
    "shuffle.partitions": "spark.sql.shuffle.partitions",
    "serializer": "spark.serializer",
}
