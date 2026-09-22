import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("Mixed06_CustomerRetention")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_customer_retention"
os.makedirs(OUT_DIR, exist_ok=True)

# Sample customers dataset
customers_data = [
    (1, "Aarav", "Sharma"),
    (2, "Meera", "Patel"),
    (3, "Rohan", "Verma"),
    (4, "Priya", "Nair"),
    (5, "Ananya", "Iyer"),
]
customers = spark.createDataFrame(customers_data, ["customer_id", "first_name", "last_name"])

# Sample orders dataset
orders_data = [
    (101, 1, "2025-01-10"),
    (102, 1, "2025-02-14"),
    (103, 1, "2025-03-20"),
    (104, 2, "2025-01-15"),
    (105, 2, "2025-03-05"),
    (106, 3, "2025-01-20"),
    (107, 3, "2025-02-28"),
    (108, 4, "2024-06-10"),
    (109, 5, "2026-08-15"),
]
orders = spark.createDataFrame(orders_data, ["order_id", "customer_id", "order_date"])
orders = orders.withColumn("order_date", F.to_date("order_date"))
orders.cache()

# Sequence orders per customer
by_cust_date = Window.partitionBy("customer_id").orderBy("order_date")
orders_ranked = orders.withColumn("order_seq", F.row_number().over(by_cust_date))

# Extract first and second order dates
first_orders = orders_ranked.filter(F.col("order_seq") == 1).select("customer_id", F.col("order_date").alias("first_order_date"))
second_orders = orders_ranked.filter(F.col("order_seq") == 2).select("customer_id", F.col("order_date").alias("second_order_date"))

# Calculate days between first and second orders
first_second = (
    first_orders
    .join(second_orders, "customer_id", "left")
    .withColumn("days_between_first_second", F.datediff("second_order_date", "first_order_date"))
)
first_second.show(truncate=False)

# Identify repeat customers and total order counts
order_counts = orders.groupBy("customer_id").agg(F.count("*").alias("num_orders"))
repeat_customers = order_counts.filter(F.col("num_orders") > 1)
repeat_customers.show()

# Find customers who ordered in consecutive months
orders_month = (
    orders
    .withColumn("year_month", F.date_format("order_date", "yyyy-MM"))
    .select("customer_id", "year_month")
    .distinct()
)

w_month = Window.partitionBy("customer_id").orderBy("year_month")
orders_month_lag = (
    orders_month
    .withColumn("prev_month", F.lag("year_month", 1).over(w_month))
    .withColumn(
        "months_apart",
        F.round(
            F.months_between(
                F.to_date(F.concat(F.col("year_month"), F.lit("-01"))),
                F.to_date(F.concat(F.col("prev_month"), F.lit("-01")))
            )
        )
    )
)
consecutive_customers = orders_month_lag.filter(F.col("months_apart") == 1).select("customer_id").distinct()
consecutive_customers.show()

# Monthly active customers (MAC)
mac = (
    orders
    .withColumn("year_month", F.date_format("order_date", "yyyy-MM"))
    .groupBy("year_month")
    .agg(F.countDistinct("customer_id").alias("monthly_active_customers"))
    .orderBy("year_month")
)
mac.show()

# Vectorized month-over-month retention calculation
month_customers = (
    orders
    .withColumn("year_month", F.date_format("order_date", "yyyy-MM"))
    .select("customer_id", "year_month")
    .distinct()
    .cache()
)

month_totals = month_customers.groupBy("year_month").agg(F.countDistinct("customer_id").alias("total_customers"))

next_month_df = month_customers.withColumn(
    "next_month",
    F.date_format(F.add_months(F.to_date(F.concat(F.col("year_month"), F.lit("-01"))), 1), "yyyy-MM")
)

retained_next_month = (
    next_month_df.alias("a")
    .join(
        month_customers.alias("b"),
        (F.col("a.next_month") == F.col("b.year_month")) & (F.col("a.customer_id") == F.col("b.customer_id"))
    )
    .groupBy(F.col("a.next_month").alias("month"))
    .agg(F.countDistinct(F.col("a.customer_id")).alias("retained_customers"))
)

retention_df = (
    retained_next_month
    .join(
        month_totals.withColumnRenamed("year_month", "prev_month_key"),
        F.col("month") == F.date_format(F.add_months(F.to_date(F.concat(F.col("prev_month_key"), F.lit("-01"))), 1), "yyyy-MM")
    )
    .withColumn(
        "retention_percentage",
        F.round((F.col("retained_customers") / F.col("total_customers")) * 100, 2)
    )
    .select(
        "month",
        F.col("prev_month_key").alias("previous_month"),
        "retained_customers",
        F.col("total_customers").alias("previous_month_customers"),
        "retention_percentage"
    )
    .orderBy("month")
)
retention_df.show(truncate=False)

# Identify customers inactive for 90 or more days
last_order = (
    orders
    .groupBy("customer_id")
    .agg(F.max("order_date").alias("last_order_date"))
)
inactive_90 = (
    last_order
    .withColumn("days_inactive", F.datediff(F.current_date(), "last_order_date"))
    .filter(F.col("days_inactive") > 90)
)
inactive_90.show(truncate=False)

# Write month-over-month retention results to Parquet
retention_df.write.mode("overwrite").parquet(f"{OUT_DIR}/customer_retention_report")

# Read Parquet file back to verify write
df_saved = spark.read.parquet(f"{OUT_DIR}/customer_retention_report")
df_saved.show(truncate=False)

orders.unpersist()
month_customers.unpersist()

spark.stop()