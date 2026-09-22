import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("DeloitteRoutes")
    .master("local[2]")
    .getOrCreate()
)

print("=" * 60)
print("Deloitte - Unique undirected route combinations")
print("=" * 60)

#  data
routes_data = [
    ("Delhi", "Pune", 1400),
    ("Pune", "Delhi", 1400),
    ("Bangalore", "Chennai", 350),
    ("Mumbai", "Ahmedabad", 500),
    ("Chennai", "Bangalore", 350),
    ("Patna", "Ranchi", 300),
]
columns = ["Start_Location", "End_Location", "Distance"]
routes = spark.createDataFrame(routes_data, columns)

# Normalization

normalized_routes = (
    routes
    .withColumn("City_A", F.least(F.col("Start_Location"), F.col("End_Location")))
    .withColumn("City_B", F.greatest(F.col("Start_Location"), F.col("End_Location")))
)

# Drop duplicates
unique_routes = (
    normalized_routes
    .dropDuplicates(["City_A", "City_B"])
    .select(
        F.col("City_A").alias("Start_Location"),
        F.col("City_B").alias("End_Location"),
        "Distance"
    )
)

unique_routes.show()