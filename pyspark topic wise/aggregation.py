import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("Assignment06_Aggregations")
    .master("local[2]")
    .getOrCreate()
)

# Sample orders dataset
orders_data = [
    (101, 1, 7500.0, 500.0, 150.0, "Completed", "UPI", "Karnataka", "2025-01-15"),
    (102, 2, 1200.0, 100.0,  50.0, "Cancelled", "Card", "Maharashtra", "2025-01-20"),
    (103, 1, 9500.0, 800.0, 200.0, "Completed", "UPI", "Karnataka", "2025-02-10"),
    (104, 3,  450.0,   0.0,  30.0, "Pending", "UPI", "Delhi", "2025-02-14"),
    (105, 2, 6000.0, 600.0, 100.0, "Completed", "NetBanking", "Maharashtra", "2025-03-01"),
    (106, 4, 3200.0, 200.0,  80.0, "Completed", "Card", "Tamil Nadu", "2025-03-05"),
]

columns = [
    "order_id", "customer_id", "total_amount", "discount_amount",
    "shipping_cost", "order_status", "payment_method", "shipping_state", "order_date"
]

orders = spark.createDataFrame(orders_data, columns)
orders = orders.withColumn("order_date", F.to_date("order_date"))
orders.cache()

# Overall summary metrics
orders.select(
    F.count("*").alias("total_orders"),
    F.round(F.sum("total_amount"), 2).alias("total_revenue"),
    F.round(F.avg("total_amount"), 2).alias("avg_order_value"),
    F.round(F.min("total_amount"), 2).alias("min_order_value"),
    F.round(F.max("total_amount"), 2).alias("max_order_value"),
    F.round(F.sum("discount_amount"), 2).alias("total_discount"),
    F.round(F.sum("shipping_cost"), 2).alias("total_shipping_cost"),
).show()

# Order count by status
(
    orders
    .groupBy("order_status")
    .agg(F.count("*").alias("order_count"))
    .orderBy("order_status")
    .show()
)

# Total revenue by state
(
    orders
    .groupBy("shipping_state")
    .agg(F.round(F.sum("total_amount"), 2).alias("revenue"))
    .orderBy(F.col("revenue").desc())
    .show(10)
)

# Total revenue by payment method
(
    orders
    .groupBy("payment_method")
    .agg(F.round(F.sum("total_amount"), 2).alias("revenue"))
    .orderBy(F.col("revenue").desc())
    .show()
)

# Average order value by customer
(
    orders
    .groupBy("customer_id")
    .agg(F.round(F.avg("total_amount"), 2).alias("avg_order_value"))
    .orderBy(F.col("avg_order_value").desc())
    .show(10)
)

# Maximum single order value by customer
(
    orders
    .groupBy("customer_id")
    .agg(F.round(F.max("total_amount"), 2).alias("max_order_value"))
    .orderBy(F.col("max_order_value").desc())
    .show(10)
)

# Monthly revenue
orders_month = orders.withColumn("year_month", F.date_format("order_date", "yyyy-MM"))

(
    orders_month
    .groupBy("year_month")
    .agg(F.round(F.sum("total_amount"), 2).alias("revenue"))
    .orderBy("year_month")
    .show(20)
)

# Monthly order volume
(
    orders_month
    .groupBy("year_month")
    .agg(F.count("*").alias("order_count"))
    .orderBy("year_month")
    .show(20)
)

# Revenue breakdown by state and payment 
(
    orders
    .groupBy("shipping_state", "payment_method")
    .agg(F.round(F.sum("total_amount"), 2).alias("revenue"))
    .orderBy("shipping_state", "payment_method")
    .show(20)
)

spark.stop()