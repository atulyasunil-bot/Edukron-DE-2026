import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("KPMGRidesAnalytics")
    .master("local[2]")
    .getOrCreate()
)

print("=" * 60)
print("KPMG - Rides won / lost per brand")
print("=" * 60)

# data
kpmg_data = [
    ("A", "B", "C", "B"),
    ("B", "C", "E", "E"),
    ("C", "A", "D", "D"),
    ("D", "E", "A", "A"),
    ("F", "B", "C", "F"),
]
columns = ["Brand_1", "Brand_2", "Brand_3", "Winner"]
kpmg = spark.createDataFrame(kpmg_data, columns)

# flatten

participants = kpmg.select(
    "Winner",
    F.explode(F.array("Brand_1", "Brand_2", "Brand_3")).alias("Brand")
)

# wins and losses
scored = (
    participants
    .withColumn("is_win", F.when(F.col("Brand") == F.col("Winner"), 1).otherwise(0))
    .withColumn("is_loss", F.when(F.col("Brand") != F.col("Winner"), 1).otherwise(0))
)

# Group by
result = (
    scored
    .groupBy("Brand")
    .agg(
        F.count("*").alias("NO_OF_RIDES"),
        F.sum("is_win").alias("RIDES_WON"),
        F.sum("is_loss").alias("RIDES_LOST")
    )
    .orderBy("Brand")
)

result.show()