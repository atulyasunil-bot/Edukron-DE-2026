import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Assignment04_WithColumnRenamed")
    .master("local[2]")
    .getOrCreate()
)

# Sample customers dataset
customers_data = [
    (1, "Aarav", "Sharma", "2024-01-15", "Premium"),
    (2, "Meera", "Patel", "2024-02-20", "Standard"),
    (3, "Rohan", "Verma", "2024-03-05", "Basic"),
    (4, "Priya", "Nair", "2024-03-12", "Premium"),
    (5, "Karthik", "Rao", "2024-04-01", "Standard"),
]
columns = ["customer_id", "first_name", "last_name", "registration_date", "customer_segment"]
customers = spark.createDataFrame(customers_data, columns)

# Display original schema
customers.printSchema()

# Rename columns using withColumnRenamed
customers_renamed = (
    customers
    .withColumnRenamed("customer_id", "cust_id")
    .withColumnRenamed("first_name", "fname")
    .withColumnRenamed("last_name", "lname")
    .withColumnRenamed("registration_date", "signup_date")
    .withColumnRenamed("customer_segment", "segment")
)

# Display modified schema and sample rows
customers_renamed.printSchema()
customers_renamed.show(truncate=False)

spark.stop()