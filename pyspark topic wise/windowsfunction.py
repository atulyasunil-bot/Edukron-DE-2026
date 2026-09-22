import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("Assignment07_WindowFunctions")
    .master("local[2]")
    .getOrCreate()
)

# Sample orders dataset
orders_data = [
    (101, 1, 1500.0, "2025-01-10"),
    (102, 1, 2500.0, "2025-01-25"),
    (103, 1, 2000.0, "2025-02-15"),
    (104, 1, 3500.0, "2025-03-01"),
    (105, 2,  800.0, "2025-01-12"),
    (106, 2,  600.0, "2025-02-18"),
    (107, 3, 5000.0, "2025-01-05"),
    (108, 3, 4500.0, "2025-02-20"),
    (109, 3, 7000.0, "2025-03-10"),
    (110, 4, 1200.0, "2025-01-15"),
]

columns = ["order_id", "customer_id", "total_amount", "order_date"]
orders = spark.createDataFrame(orders_data, columns)
orders = orders.withColumn("order_date", F.to_date("order_date"))
orders.cache()

# Window specifications
by_customer_date = Window.partitionBy("customer_id").orderBy("order_date")
by_customer_date_desc = Window.partitionBy("customer_id").orderBy(F.col("order_date").desc())
running_by_customer = (
    Window.partitionBy("customer_id")
    .orderBy("order_date")
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
)

# Customer first and latest order dates
orders_with_dates = (
    orders
    .withColumn("first_order_date", F.first("order_date").over(by_customer_date))
    .withColumn("latest_order_date", F.first("order_date").over(by_customer_date_desc))
)
orders_with_dates.select("customer_id", "order_id", "order_date", "first_order_date", "latest_order_date").show()

# Rank customers based on total spending
customer_totals = (
    orders
    .groupBy("customer_id")
    .agg(F.round(F.sum("total_amount"), 2).alias("total_spending"))
)

customer_rank = (
    customer_totals
    .withColumn("spend_rank", F.rank().over(Window.orderBy(F.col("total_spending").desc())))
    .orderBy("spend_rank")
)
customer_rank.show()

# Rank orders within each customer and pick top 3
orders_ranked = orders.withColumn(
    "order_rank_within_customer",
    F.row_number().over(Window.partitionBy("customer_id").orderBy(F.col("total_amount").desc()))
)

top3_per_customer = (
    orders_ranked
    .filter(F.col("order_rank_within_customer") <= 3)
    .select("customer_id", "order_id", "total_amount", "order_rank_within_customer")
    .orderBy("customer_id", "order_rank_within_customer")
)
top3_per_customer.show()

# Running total revenue per customer
running_revenue = orders.withColumn(
    "running_revenue",
    F.round(F.sum("total_amount").over(running_by_customer), 2)
)
running_revenue.select("customer_id", "order_date", "total_amount", "running_revenue").show()

# lead and difference versus previous order
lag_lead = (
    orders
    .withColumn("prev_order_amount", F.lag("total_amount", 1).over(by_customer_date))
    .withColumn("next_order_amount", F.lead("total_amount", 1).over(by_customer_date))
    .withColumn(
        "diff_vs_previous",
        F.round(F.col("total_amount") - F.lag("total_amount", 1).over(by_customer_date), 2)
    )
)
(
    lag_lead
    .select("customer_id", "order_date", "total_amount", "prev_order_amount", "next_order_amount", "diff_vs_previous")
    .orderBy("customer_id", "order_date")
    .show()
)

# Cumulative order count per customer
cum_count = orders.withColumn(
    "cumulative_order_count",
    F.row_number().over(by_customer_date)
)
cum_count.select("customer_id", "order_date", "cumulative_order_count").show()

# Customers whose latest order value is greater than their previous order
bonus = (
    lag_lead
    .withColumn("row_desc", F.row_number().over(by_customer_date_desc))
    .filter((F.col("row_desc") == 1) & (F.col("total_amount") > F.col("prev_order_amount")))
)
bonus.select("customer_id", "order_date", "total_amount", "prev_order_amount").show()


spark.stop()