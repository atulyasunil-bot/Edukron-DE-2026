import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("AmazonOrderReview")
    .master("local[2]")
    .getOrCreate()
)

print("=" * 60)
print("Q7: Amazon - Flag orders with >2 failed payments")
print("=" * 60)

# Tables
orders_data = [
    (101, 1, "10/01/2024", 250),
    (102, 2, "12/01/2024", 450),
    (103, 3, "15/01/2024", 700),
]
orders = spark.createDataFrame(orders_data, ["OrderID", "CustomerID", "OrderDate", "Amount"])

payments_data = [
    (1, 101, "10/01/2024", "Failed"),
    (2, 101, "11/01/2024", "Failed"),
    (3, 101, "12/01/2024", "Failed"),
    (4, 102, "12/01/2024", "Success"),
    (5, 103, "15/01/2024", "Failed"),
    (6, 103, "16/01/2024", "Failed"),
]
payments = spark.createDataFrame(payments_data, ["PaymentID", "OrderID", "PaymentDate", "Status"])

# Filter for 'Failed' attempts and counting how many attempt
failed_attempts = (
    payments
    .filter(F.col("Status") == "Failed")
    .groupBy("OrderID")
    .agg(F.count("PaymentID").alias("failed_count"))
)

# using a LEFT JOIN
flagged_orders = (
    orders
    .join(failed_attempts, on="OrderID", how="left")
# for zero error
    .fillna({"failed_count": 0})
# If failed more than 2 times -> Flag 'Yes', otherwise 'No'
    .withColumn(
        "Flag",
        F.when(F.col("failed_count") > 2, "Yes").otherwise("No")
    )
    .drop("failed_count")
    .orderBy("OrderID")
)

flagged_orders.show()