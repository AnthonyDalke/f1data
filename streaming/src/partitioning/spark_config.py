config = {
    "master": {
        "spark.driver.memory": "6g",
        "spark.sql.shuffle.partitions": "6",
        "spark.serializer": "org.apache.spark.serializer.JavaSerializer",
        "spark.ui.port": "4040",},
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

test = {
    "master": {"local": {variable}},
    "driver.memory": {
        "spark.driver.memory": {variable},
    },
    "shuffle.partitions": {"spark.sql.shuffle.partitions": str(variable),
    "serializer": {
        "spark.serializer": f"""
        'org.apache.spark.serializer.KryoSerializer'
        if {variable} == 'kryo'
        else 'org.apache.spark.serializer.JavaSerializer'
        """
    },
}
