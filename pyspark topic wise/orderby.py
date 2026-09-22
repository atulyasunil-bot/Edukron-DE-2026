import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("Assignment09_OrderBy")
    .master("local[2]")
    .getOrCreate()
)

# Sample customers dataset
customers_data = [
    (1, "Aarav", "Sharma"),
    (2, "Meera", "Patel"),
    (3, "Rohan", "Verma"),
    (4, "Priya", "Nair"),
]
customers = spark.createDataFrame(customers_data, ["customer_id", "first_name", "last_name"])

# Sample orders dataset
orders_data = [
    (101, 1, 1500.0, "Completed", "Karnataka", "Bengaluru", "2025-01-15"),
    (102, 2, 8500.0, "Pending", "Maharashtra", None, "2025-02-10"),
    (103, 1, 450.0, "Completed", "Karnataka", "Mysuru", "2024-11-20"),
    (104, 3, 12000.0, "Cancelled", "Delhi", "Delhi", "2025-03-05"),
    (105, 2, 3200.0, "Completed", "Maharashtra", "Pune", "2024-12-01"),
    (106, 4, 750.0, "Pending", "Tamil Nadu", None, "2025-01-25"),
]
columns = [
    "order_id", "customer_id", "total_amount", "order_status",
    "shipping_state", "shipping_city", "order_date"
]
orders = spark.createDataFrame(orders_data, columns)
orders = orders.withColumn("order_date", F.to_date("order_date"))
orders.cache()

# Ascending order by total amount
orders.orderBy("total_amount").show()

# Descending order by total amount
orders.orderBy(F.col("total_amount").desc()).show()

# Descending order by order date
orders.orderBy(F.col("order_date").desc()).show()

# Multi-column sort by shipping state and total amount
orders.orderBy("shipping_state", "total_amount").show()

# Sort order status ascending and total amount descending
orders.orderBy(F.col("order_status").asc(), F.col("total_amount").desc()).show()

# Ascending order with null values appearing first
orders.orderBy(F.col("shipping_city").asc_nulls_first()).show()

# Ascending order with null values appearing last
orders.orderBy(F.col("shipping_city").asc_nulls_last()).show()

# Top highest value orders
top_orders = orders.orderBy(F.col("total_amount").desc()).limit(3)
top_orders.show()

# Oldest orders by order date
oldest_orders = orders.orderBy("order_date").limit(3)
oldest_orders.show()

# Sort customers by total spending with nulls last
customer_spend = (
    orders
    .groupBy("customer_id")
    .agg(F.round(F.sum("total_amount"), 2).alias("total_spending"))
)

(
    customers
    .join(customer_spend, "customer_id", "left")
    .orderBy(F.col("total_spending").desc_nulls_last())
    .select("customer_id", "first_name", "last_name", "total_spending")
    .show()
)

spark.stop()