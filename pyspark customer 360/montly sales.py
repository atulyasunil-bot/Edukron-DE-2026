import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("Mixed04_MonthlySalesReport")
    .master("local[2]")
    .getOrCreate()
)

OUT_DIR = "./output_monthly_sales_report"
os.makedirs(OUT_DIR, exist_ok=True)

# Sample orders dataset
orders_data = [
    (101, 1, 12000.0, 1000.0, "Completed", "2025-01-10"),
    (102, 2,  4500.0,  300.0, "Completed", "2025-01-18"),
    (103, 1,  8000.0,  500.0, "Cancelled", "2025-01-25"),
    (104, 3, 15000.0, 1200.0, "Completed", "2025-02-05"),
    (105, 2,  7000.0,  600.0, "Completed", "2025-02-14"),
    (106, 4, 22000.0, 2000.0, "Completed", "2025-03-02"),
    (107, 1, 18000.0, 1500.0, "Completed", "2025-03-20"),
    (108, 5,  3500.0,  200.0, "Completed", "2025-04-10"),
    (109, 3,  9500.0,  800.0, "Cancelled", "2025-04-18"),
]
orders_cols = ["order_id", "customer_id", "total_amount", "discount_amount", "order_status", "order_date"]
orders = spark.createDataFrame(orders_data, orders_cols)
orders = orders.withColumn("order_date", F.to_date("order_date"))

# Add year-month column
orders_m = orders.withColumn("month", F.date_format("order_date", "yyyy-MM"))

# Compute cohort month for each customer
first_order_month = orders_m.groupBy("customer_id").agg(F.min("month").alias("first_month"))

# Aggregate base monthly metrics
monthly = orders_m.groupBy("month").agg(
    F.count("*").alias("total_orders"),
    F.count(F.when(F.col("order_status") == "Completed", True)).alias("completed_orders"),
    F.count(F.when(F.col("order_status") == "Cancelled", True)).alias("cancelled_orders"),
    F.round(F.sum("total_amount"), 2).alias("total_revenue"),
    F.round(F.sum("discount_amount"), 2).alias("total_discount"),
    F.round(F.avg("total_amount"), 2).alias("average_order_value"),
    F.countDistinct("customer_id").alias("unique_customers"),
)

# Calculate new acquisition counts per month
new_customers_per_month = (
    first_order_month
    .groupBy("first_month")
    .agg(F.countDistinct("customer_id").alias("new_customers"))
    .withColumnRenamed("first_month", "month")
)

monthly = monthly.join(new_customers_per_month, "month", "left").fillna({"new_customers": 0})

# Window definitions
w = Window.orderBy("month")
cum_window = Window.orderBy("month").rowsBetween(Window.unboundedPreceding, Window.currentRow)

# Month-over-month comparisons and cumulative revenue
monthly = (
    monthly
    .withColumn("previous_month_revenue", F.lag("total_revenue", 1).over(w))
    .withColumn("revenue_difference", F.round(F.col("total_revenue") - F.col("previous_month_revenue"), 2))
    .withColumn(
        "revenue_growth_percentage",
        F.round(
            F.when(
                F.col("previous_month_revenue") > 0,
                ((F.col("total_revenue") - F.col("previous_month_revenue")) / F.col("previous_month_revenue")) * 100
            ).otherwise(0.0),
            2
        )
    )
    .withColumn("cumulative_revenue", F.round(F.sum("total_revenue").over(cum_window), 2))
    .orderBy("month")
)

# Display chronological monthly report
monthly.show(truncate=False)

# Highest revenue month
monthly.orderBy(F.col("total_revenue").desc()).limit(1).show(truncate=False)

# Lowest revenue month
monthly.orderBy(F.col("total_revenue").asc()).limit(1).show(truncate=False)

# Write report to Parquet
monthly.write.mode("overwrite").parquet(f"{OUT_DIR}/monthly_sales_report")

# Read Parquet file back to verify write
df_saved = spark.read.parquet(f"{OUT_DIR}/monthly_sales_report")
df_saved.select("month", "total_revenue", "revenue_growth_percentage", "cumulative_revenue").show(truncate=False)

spark.stop()